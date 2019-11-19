# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/molotov>
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import jinja2
import logging
import os
import random
import re
import requests
import string
import tempfile
from contextlib import closing
from datetime import datetime, timedelta
import werkzeug

import odoo
from odoo import exceptions, fields, http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.service import db
from odoo.sql_db import db_connect
from odoo.tools import config, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import str2bool
from odoo.addons import web
from odoo.addons.web.controllers.main import DBNAME_PATTERN
from odoo.release import version_info

try:
    import boto3
    import botocore
    from pretty_bad_protocol import gnupg
except ImportError as err:
    logging.getLogger(__name__).debug(err)

_logger = logging.getLogger(__name__)
path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
loader = jinja2.FileSystemLoader(path)
env = jinja2.Environment(loader=loader, autoescape=True)
BACKUP_SERVICE_ENDPOINT = 'https://odoo-backup.sh'

# module -> config parameter name
EXTRA_MODULES = {
    'odoo_backup_sh_dropbox': lambda env: env['ir.config_parameter'].get_param('odoo_backup_sh_dropbox.dropbox_access_token'),
    'odoo_backup_sh_google_disk': lambda env: env['ir.config_parameter'].get_param('odoo_backup_sh_google_disk.service_account_key'),
}


class BackupDatabase(web.controllers.main.Database):

    def _render_template(self, **d):
        res = super(BackupDatabase, self)._render_template(**d)
        # Show button 'Restore via Odoo-backup.sh' on web/database/manager and web/database/selector pages
        place_for_backup_button = re.search('Set Master Password</button>.*\n.*</div>', res)
        if place_for_backup_button:
            place_for_backup_button = place_for_backup_button.end()
        else:
            place_for_backup_button = re.search(
                '<a role="button" data-toggle="modal" data-target=".o_database_restore" class="btn btn-link">', res)
            if place_for_backup_button:
                place_for_backup_button = place_for_backup_button.start()
        if place_for_backup_button:
            d['list_db'] = config['list_db']
            d['databases'] = []
            try:
                d['databases'] = http.db_list()
            except odoo.exceptions.AccessDenied:
                monodb = http.db_monodb()
                if monodb:
                    d['databases'] = [monodb]
            backup_button = env.get_template("backup_button.html").render(d)
            res = res[:place_for_backup_button] + backup_button + res[place_for_backup_button:]
        return res


class CloudConfigStoreAbstract:
    def _get_one(self, key, env=None):
        raise NotImplementedError()

    def get(self, keys, env=None):
        if isinstance(keys, str):
            return self._get_one(keys, env=env)
        elif isinstance(keys, list) or isinstance(keys, tuple):
            return dict(
                (k, self._get_one(k, env=env)) for k in keys
            )
        else:
            raise ValueError("Unexpected type: {}".format(type(keys)))

    def set(self, key, value):
        raise NotImplementedError()


class CloudConfigStoreBackend(CloudConfigStoreAbstract):
    def _get_one(self, key, env=None):
        return (env or request.env)['ir.config_parameter'].sudo().get_param(key)

    def set(self, key, value):
        request.env['ir.config_parameter'].sudo().set_param(key, value)


class CloudConfigStoreFrontend(CloudConfigStoreAbstract):
    def _get_one(self, key, env=None):
        return request.session.get(key)

    def set(self, key, value):
        request.session[key] = value


cloud_config_stores = {
    'frontend': CloudConfigStoreFrontend(),
    'backend': CloudConfigStoreBackend(),
}


class BackupController(http.Controller):

    @classmethod
    def get_cloud_params(cls, redirect=None, call_from='backend', update=True, env=None):
        mandadory_params = cloud_config_stores[call_from].get([
            'odoo_backup_sh.s3_bucket_name',
            'odoo_backup_sh.aws_access_key_id',
            'odoo_backup_sh.aws_secret_access_key',
        ], env=env)
        cloud_params = cloud_config_stores[call_from].get([
            'odoo_backup_sh.user_key',
            'odoo_backup_sh.private_s3_dir',
            'odoo_backup_sh.odoo_oauth_uid'
        ], env=env)
        cloud_params.update(mandadory_params)
        if update and (len(mandadory_params) == 0 or not all(mandadory_params.values())):
            if redirect:
                cloud_params = cls.update_cloud_params(cloud_params, redirect, call_from)
            else:
                # This case occurs when we cannot pass the redirect param, ex. the request was sent by a cron
                raise UserError(_("You don't have credentials to access to cloud storage. "
                                  "Please go to the backup dashboard menu"))
        return cloud_params

    @classmethod
    def update_cloud_params(cls, cloud_params, redirect, call_from):
        user_key = cloud_params['odoo_backup_sh.user_key']
        if not user_key:
            user_key = ''.join(random.choice(string.hexdigits) for _ in range(30))
            cloud_config_stores[call_from].set('odoo_backup_sh.user_key', user_key)

        # You can set the verify parameter to False and requests will ignore SSL verification.
        try:
            res = requests.get(BACKUP_SERVICE_ENDPOINT + '/get_cloud_params', params={
                'user_key': user_key,
                'redirect': redirect,
            }, verify=True)
            _logger.debug('/get_cloud_params returned: %s', res.text)
            cloud_params = res.json()
        except Exception:
            _logger.exception('Failed to load cloud params')

        if 'insufficient_credit_error' in cloud_params and call_from == 'backend':
            existing_msg = request.env['odoo_backup_sh.notification'].sudo().search(
                [('type', '=', 'insufficient_credits'), ('is_read', '=', False)])
            notification_vals = {
                'date_create': datetime.now(),
                'type': 'insufficient_credits',
                'message': cloud_params['insufficient_credit_error']
            }
            if existing_msg:
                existing_msg.write(notification_vals)
            else:
                request.env['odoo_backup_sh.notification'].sudo().create(notification_vals)
        elif all(param not in cloud_params for param in ['auth_link', 'insufficient_credit_error']):
            for option, value in cloud_params.items():
                cloud_config_stores[call_from].set(option, value)
            if call_from == 'frontend':
                # After creating a new IAM user we have to make a delay for the AWS.
                # Otherwise AWS don't determine the user just created by it and returns an InvalidAccessKeyId error.
                # FIXME
                # time.sleep(20)
                pass
            else:
                request.env['odoo_backup_sh.notification'].sudo().search(
                    [('type', 'in', ['insufficient_credits', 'forecast_insufficient_credits']), ('is_read', '=', False)]
                ).unlink()
        return cloud_params

    # TODO: don't use /web/database/ prefix
    @http.route('/web/database/backup', type='http', auth='user')
    def download_backup(self, backup_id, **kwargs):
        backup_info_record = request.env['odoo_backup_sh.backup_info'].search([
            ('id', '=', backup_id),
            ('storage_service', '=', 'odoo_backup_sh'),
        ])
        backup_info_record.ensure_one()
        backup_info_record.assert_user_can_download_backup()
        path = backup_info_record.backup_path
        backup_filename = backup_info_record.backup_filename
        backup_key = '%s/%s' % (path, backup_filename)
        cloud_params = self.get_cloud_params(request.httprequest.url, call_from='backend')
        backup_object = BackupCloudStorage.get_object(cloud_params, key=backup_key)
        return http.Response(
            backup_object['Body'].iter_chunks(),
            headers={
                'Content-Disposition': 'attachment; filename="{0}"'.format(backup_filename),
                'Content-Type': 'application/octet-stream',
            }
        )

    @http.route('/web/database/backups', type='http', auth="none")
    def backup_list(self):
        page_values = {
            'backup_list': [],
            'pattern': DBNAME_PATTERN,
            'insecure': config.verify_admin_password('admin')
        }
        if not config['list_db']:
            page_values['error'] = 'The database manager has been disabled by the administrator'
            return env.get_template("backup_list.html").render(page_values)
        cloud_params = self.get_cloud_params(request.httprequest.url, call_from='frontend')
        if 'auth_link' in cloud_params:
            return "<html><head><script>window.location.href = '%s';</script></head></html>" % cloud_params['auth_link']
        elif 'insufficient_credit_error' in cloud_params:
            page_values['error'] = cloud_params['insufficient_credit_error']
            return env.get_template("backup_list.html").render(page_values)
        backup_list = BackupCloudStorage.get_all_files(cloud_params)
        if 'reload_page' in backup_list:
            page_values['error'] = 'AWS needs some time to activate s3 credentials. Please refresh the page in 30 seconds.'
            return env.get_template("backup_list.html").render(page_values)
        page_values['backup_list'] = [name for name, _ in backup_list['all_files'] if not name.endswith('.info')]
        return env.get_template("backup_list.html").render(page_values)

    @http.route('/web/database/restore_via_odoo_backup_sh', type='http', auth="none", methods=['POST'], csrf=False)
    def restore_via_odoo_backup_sh(self, master_pwd, backup_file_name, name, encryption_password, copy=False):
        if config['admin_passwd'] != master_pwd:
            return env.get_template("backup_list.html").render(error="Incorrect master password")
        if os.path.exists(config.filestore(name)):
            return env.get_template("backup_list.html").render(
                error='Filestore for database "{}" already exists. Please choose another database name'.format(name)
            )
        cloud_params = self.get_cloud_params(request.httprequest.url, call_from='frontend')
        backup_object = BackupCloudStorage.get_object(cloud_params, filename=backup_file_name)
        backup_file = tempfile.NamedTemporaryFile()
        backup_file.write(backup_object['Body'].read())
        if backup_file_name.split('|')[0][-4:] == '.enc':
            if not encryption_password:
                raise UserError(_(
                    'The backup are encrypted. But encryption password is not found. Please check your module settings.'
                ))
            # GnuPG ignores the --output parameter with an existing file object as value
            decrypted_backup_file = tempfile.NamedTemporaryFile()
            decrypted_backup_file_name = decrypted_backup_file.name
            os.unlink(decrypted_backup_file_name)
            backup_file.seek(0)
            r = gnupg.GPG().decrypt_file(backup_file, passphrase=encryption_password, output=decrypted_backup_file_name)
            if not r.ok:
                error = 'gpg: {0}'.format(r.status)
                if not r.valid:
                    error += ". Maybe wrong password?"
                return env.get_template("backup_list.html").render(error=error)
            backup_file = open(decrypted_backup_file_name, 'rb')
        try:
            db.restore_db(name, backup_file.name, str2bool(copy))
            # Make all auto backup cron records inactive
            with closing(db_connect(name).cursor()) as cr:
                cr.autocommit(True)
                try:
                    cr.execute("""
                        UPDATE ir_cron SET active=false
                        WHERE active=true AND id IN (SELECT ir_cron_id FROM odoo_backup_sh_config_cron);

                        UPDATE odoo_backup_sh_config SET active=false WHERE active=true;
                    """)
                except Exception:
                    pass
            return http.local_redirect('/web/database/manager')
        except Exception as e:
            error = "Database restore error: %s" % (str(e) or repr(e))
            return env.get_template("backup_list.html").render(error=error)
        finally:
            os.unlink(backup_file.name)

    @http.route('/odoo_backup_sh/get_s3_credentials', type="http", auth='user')
    def get_s3_credentials(self, redirect):
        cloud_params = self.get_cloud_params(request.httprequest.url, call_from='backend')
        if 'auth_link' in cloud_params:
            return werkzeug.utils.redirect(cloud_params.get('auth_link'))
        else:
            return werkzeug.utils.redirect(redirect)

    @http.route('/odoo_backup_sh/fetch_dashboard_data', type="json", auth='user')
    def fetch_dashboard_data(self):
        date_month_before = datetime.now().date() - timedelta(days=29)
        date_list = [date_month_before + timedelta(days=x) for x in range(30)]
        last_month_domain = [('date', '>=', datetime.strftime(date_list[0], DEFAULT_SERVER_DATE_FORMAT))]
        values = request.env['odoo_backup_sh.remote_storage'].search(last_month_domain).sorted(key='date')
        usage_values = {
            r.date: r.total_used_remote_storage for r in values
        }
        for date in date_list:
            if date not in usage_values:
                if date_list.index(date) == 0:
                    usage_values[date] = 0
                else:
                    usage_values[date] = usage_values.get(date_list[date_list.index(date) - 1], 0)
        dashboard_data = {
            'remote_storage_usage_graph_values': [{
                'key': 'Remote Storage Usage',
                'values': [{
                    0: fields.Date.to_string(day),
                    1: usage_values[day]
                } for day in date_list]
            }]
        }
        s3_usage_values = {
            r.date: r.s3_used_remote_storage for r in values
        }
        for date in date_list:
            if date not in s3_usage_values:
                if date_list.index(date) == 0:
                    s3_usage_values[date] = 0
                else:
                    s3_usage_values[date] = s3_usage_values.get(date_list[date_list.index(date) - 1], 0)

        dashboard_data['services_storage_usage_graph_values'] = {
            'odoo_backup_sh': [{
                'key': 'Remote S3 Storage Usage',
                'values': [{
                    0: fields.Date.to_string(day),
                    1: s3_usage_values[day]
                } for day in date_list]
            }]
        }
        last_week_dates = date_list[-7:]
        backup_configs = request.env['odoo_backup_sh.config'].with_context({'active_test': False}).search_read(
            [], ['database', 'active', 'storage_service'])
        for b_config in backup_configs:
            graph_values = {date: 0 for date in last_week_dates}
            for backup in request.env['odoo_backup_sh.backup_info'].search([
                    ('database', '=', b_config['database']),
                    ('upload_datetime', '>=', datetime.strftime(last_week_dates[0], DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('storage_service', '=', b_config['storage_service'])]):
                graph_values[backup.upload_datetime.date()] += backup.backup_size
            b_config.update({
                'backups_number': request.env['odoo_backup_sh.backup_info'].search_count([
                    ('database', '=', b_config['database']), ('storage_service', '=', b_config['storage_service'])]),
                'graph': [{
                    'values': [{
                        'label': fields.Date.to_string(date),
                        'value': graph_values[date],
                    } for date in last_week_dates]
                }]
            })
        cloud_params = self.get_cloud_params(request.httprequest.url, call_from='backend', update=False)
        dashboard_data.update({
            'cloud_params': cloud_params,
            'configs': backup_configs,
            'notifications': request.env['odoo_backup_sh.notification'].search_read(
                [('is_read', '=', False)], ['id', 'date_create', 'message']),
            'up_balance_url': '%s/open_iap_recharge?user_key=%s' % (
                BACKUP_SERVICE_ENDPOINT,
                request.env['ir.config_parameter'].sudo().get_param('odoo_backup_sh.user_key')
            ),
        })
        modules = {
            'odoo_backup_sh': {
                'installed': True,
                'configured': bool(cloud_params.get('odoo_backup_sh.aws_access_key_id') or False),
                'configured_iap': bool(cloud_params.get('odoo_backup_sh.odoo_oauth_uid') or False)
            }
        }
        modules_search = request.env['ir.module.module'].search([('name', 'in', list(EXTRA_MODULES.keys()))])
        version = '%s.%s' % (version_info[0], version_info[1])
        for m in modules_search:
            installed = m.state == 'installed'
            modules[m.name] = {
                'url': "https://apps.odoo.com/apps/modules/%s/%s/" % (version, m.name),
                'installed': installed
            }
            if installed:
                modules[m.name]['configured'] = bool(EXTRA_MODULES[m.name](request.env))

        dashboard_data['modules'] = modules

        return dashboard_data


def access_control(origin_method):
    def wrapped(self, *args, **kwargs):
        try:
            return origin_method(self, *args, **kwargs)
        except botocore.exceptions.ClientError as client_error:
            if client_error.response['Error']['Code'] == 'InvalidAccessKeyId':
                # TODO: commented cause it doesn't work (request.env is not available here
                # [request.env['ir.config_parameter'].set_param(option, None) for option in ('odoo_backup_sh.aws_access_key_id', 'odoo_backup_sh.aws_secret_access_key')]
                return {'reload_page': True}
            else:
                raise exceptions.ValidationError(_(
                    "Amazon Web Services error: " + client_error.response['Error']['Message']))
    return wrapped


# TODO: would it better to move this to odoo_backup_sh.config ?
class BackupCloudStorage(http.Controller):

    @classmethod
    def get_amazon_s3_client(cls, cloud_params):
        s3_client = boto3.client('s3', aws_access_key_id=cloud_params['odoo_backup_sh.aws_access_key_id'],
                                 aws_secret_access_key=cloud_params['odoo_backup_sh.aws_secret_access_key'])
        return s3_client

    @classmethod
    def get_s3_dir(cls, cloud_params):
        if cloud_params.get('odoo_backup_sh.odoo_oauth_uid'):
            return cloud_params['odoo_backup_sh.odoo_oauth_uid']
        else:
            return cloud_params['odoo_backup_sh.private_s3_dir'] or '.'

    @classmethod
    @access_control
    def get_all_files(cls, cloud_params):
        amazon_s3_client = cls.get_amazon_s3_client(cloud_params)
        user_dir_name = '%s/' % cls.get_s3_dir(cloud_params)
        list_objects = amazon_s3_client.list_objects_v2(
            Bucket=cloud_params['odoo_backup_sh.s3_bucket_name'], Prefix=user_dir_name, Delimiter='/')
        all_files = [
            (obj['Key'].split('/')[-1], 'odoo_backup_sh')
            for obj in list_objects.get('Contents', {}) if obj.get('Size')
        ]
        _logger.debug('Files in %s: \n %s', user_dir_name, all_files)
        return {'all_files': all_files}

    @classmethod
    @access_control
    def get_object(cls, cloud_params, filename=None, key=None):
        amazon_s3_client = cls.get_amazon_s3_client(cloud_params)
        if not key:
            key = '%s/%s' % (cls.get_s3_dir(cloud_params), filename)
        _logger.debug('get_object: %s', key)
        return amazon_s3_client.get_object(Bucket=cloud_params['odoo_backup_sh.s3_bucket_name'], Key=key)

    @classmethod
    @access_control
    def put_object(cls, cloud_params, obj, obj_key):
        amazon_s3_client = cls.get_amazon_s3_client(cloud_params)
        _logger.debug('put_object: %s', obj_key)
        amazon_s3_client.put_object(Body=obj, Bucket=cloud_params['odoo_backup_sh.s3_bucket_name'], Key=obj_key)
        _logger.info('Following backup object have been put in the remote storage: %s' % obj_key)

    @classmethod
    @access_control
    def delete_objects(cls, cloud_params, s3_keys):
        objs = [{'Key': key} for key in s3_keys]

        amazon_s3_client = cls.get_amazon_s3_client(cloud_params)
        amazon_s3_client.delete_objects(
            Bucket=cloud_params['odoo_backup_sh.s3_bucket_name'], Delete={'Objects': objs})
        objects_names = [obj['Key'] for obj in objs]
        _logger.info(
            'Following backup objects have been deleted from the remote storage: %s' % ', '.join(objects_names))
