# -*- coding: utf-8 -*-
import os
import hashlib
import logging

from openerp import api, models, _
from openerp.tools.safe_eval import safe_eval
import openerp
from openerp import SUPERUSER_ID

# To avoid travis warnings
osv = openerp.osv.osv
fields = openerp.osv.fields

_logger = logging.getLogger(__name__)

try:
    import boto3
except:
    _logger.debug('boto3 package is required which is not \
    found on your installation')


class IrAttachmentNewApi(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _get_s3_settings(self, param_name, os_var_name):
        config_obj = self.env['ir.config_parameter']
        res = config_obj.get_param(param_name)
        if not res:
            res = os.environ.get(os_var_name)
            if res:
                config_obj.set_param(param_name, res)
                _logger.info('parameter {} has been created from env {}'.format(param_name, os_var_name))
        return res

    @api.model
    def _get_s3_object_url(self, s3, s3_bucket_name, key_name):
        bucket_location = s3.meta.client.get_bucket_location(Bucket=s3_bucket_name)
        location_constraint = bucket_location.get('LocationConstraint')
        domain_part = 's3' + '-' + location_constraint if location_constraint else 's3'
        object_url = "https://{0}.amazonaws.com/{1}/{2}".format(
            domain_part,
            s3_bucket_name,
            key_name)
        return object_url

    @api.model
    def _get_s3_resource(self):
        access_key_id = self._get_s3_settings('s3.access_key_id', 'S3_ACCESS_KEY_ID')
        secret_key = self._get_s3_settings('s3.secret_key', 'S3_SECRET_KEY')
        bucket_name = self._get_s3_settings('s3.bucket', 'S3_BUCKET')

        if not access_key_id or not secret_key or not bucket_name:
            _logger.info(_('Amazon S3 credentials are not defined properly. Attachments won\'t be saved on S3.'))
            return False

        s3 = boto3.resource(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_key,
            )
        bucket = s3.Bucket(bucket_name)
        if not bucket:
            s3.create_bucket(Bucket=bucket_name)
        return s3


class IrAttachment(osv.osv):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment']

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        s3 = self._get_s3_resource(cr, uid)
        condition = self._get_s3_settings(cr, uid, 's3.condition', 'S3_CONDITION')
        s3_id = None

        if condition:
            domain = [('id', '=', id)] + safe_eval(condition, mode="eval")
            search_res = self.search(cr, uid, domain, context=context)
            if search_res:
                s3_id = search_res.pop()
        else:
            s3_id = id

        attach = s3_id and self._filter_protected_attachments(cr, uid, [s3_id], context = context)

        if not s3 or not attach:
            return super(IrAttachment, self)._data_set(cr, uid, id, name, value, arg, context=context)

        if attach:
            bin_data = value and value.decode('base64') or ''
            fname = hashlib.sha1(bin_data).hexdigest()

            bucket_name = self._get_s3_settings(cr, uid, 's3.bucket', 'S3_BUCKET')
            s3.Bucket(bucket_name).put_object(
                Key=fname,
                Body=bin_data,
                ACL='public-read',
                ContentType=attach.mimetype,
                )

            vals = {
                'file_size': len(bin_data),
                'checksum': self._compute_checksum(bin_data),
                'index_content': self._index(cr, SUPERUSER_ID, bin_data, attach.datas_fname, attach.mimetype),
                'store_fname': fname,
                'db_datas': False,
                'type': 'url',
                'url': self._get_s3_object_url(cr, uid, s3, bucket_name, fname),
            }
            super(IrAttachment, self).write(cr, SUPERUSER_ID, [s3_id], vals, context=context)

        return True

    def _data_get(self, cr, uid, ids, name, arg, context=None):
        return super(IrAttachment, self)._data_get(cr, uid, ids, name, arg, context=context)

    _columns = {
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
    }
