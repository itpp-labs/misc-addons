# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import tempfile
from datetime import datetime

try:
    from dropbox.files import UploadSessionCursor
except ImportError as err:
    logging.getLogger(__name__).debug(err)

try:
    from dropbox.files import CommitInfo
except ImportError as err:
    logging.getLogger(__name__).debug(err)

from odoo import api, models, fields
from odoo.addons.odoo_backup_sh.models.odoo_backup_sh import compute_backup_filename, compute_backup_info_filename, get_backup_by_id, ModuleNotConfigured
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


CHUNK_SIZE = 4 * 1024 * 1024

_logger = logging.getLogger(__name__)
DROPBOX_STORAGE = 'dropbox'


class BackupConfig(models.Model):
    _inherit = "odoo_backup_sh.config"

    storage_service = fields.Selection(selection_add=[(DROPBOX_STORAGE, 'Dropbox')])

    @api.model
    def get_backup_list(self, cloud_params, service):
        backup_list = super(BackupConfig, self).get_backup_list(cloud_params, service) or dict()
        if service != DROPBOX_STORAGE:
            return backup_list
        # get all backups from dropbox
        try:
            DropboxService = self.env['ir.config_parameter'].get_dropbox_service()
        except ModuleNotConfigured:
            return backup_list
        folder_path = self.env['ir.config_parameter'].get_param("odoo_backup_sh_dropbox.dropbox_folder_path")
        response = DropboxService.files_list_folder(folder_path)
        drobpox_backup_list = [(r.name, DROPBOX_STORAGE) for r in response.entries]
        if 'all_files' in backup_list:
            backup_list.update({
                'all_files': backup_list['all_files'] + drobpox_backup_list
            })
        else:
            backup_list['all_files'] = drobpox_backup_list
        return backup_list

    @api.model
    def get_info_file_object(self, cloud_params, info_file_name, storage_service):
        if storage_service == DROPBOX_STORAGE:
            DropboxService = self.env['ir.config_parameter'].get_dropbox_service()
            folder_path = self.env['ir.config_parameter'].get_param("odoo_backup_sh_dropbox.dropbox_folder_path")
            full_path = "{folder_path}/{file_name}".format(
                folder_path=folder_path,
                file_name=info_file_name,
            )
            return DropboxService.files_download(full_path)
        else:
            return super(BackupConfig, self).get_info_file_object(cloud_params, info_file_name, storage_service)

    @api.model
    def create_info_file(self, info_file_object, storage_service):
        if storage_service == DROPBOX_STORAGE:
            info_file = tempfile.NamedTemporaryFile()
            info_file.write(info_file_object[1].content)
            info_file.seek(0)
            return info_file
        else:
            return super(BackupConfig, self).create_info_file(info_file_object, storage_service)

    @api.model
    def delete_remote_objects(self, cloud_params, remote_objects):
        folder_path = self.env['ir.config_parameter'].get_param("odoo_backup_sh_dropbox.dropbox_folder_path")
        DropboxService = None
        dropbox_remove_objects = []
        for file in remote_objects:
            if file[1] == DROPBOX_STORAGE:
                if not DropboxService:
                    DropboxService = self.env['ir.config_parameter'].get_dropbox_service()
                dropbox_remove_objects.append(file)
                full_path = "{folder_path}/{file_name}".format(
                    folder_path=folder_path,
                    file_name=file[0],
                )
                DropboxService.files_delete(full_path)

        return super(BackupConfig, self).delete_remote_objects(cloud_params, list(set(remote_objects) - set(dropbox_remove_objects)))

    @api.model
    def make_backup_dropbox(self, ts, name, dump_stream, info_file, info_file_content, cloud_params):
        # Upload two backup objects to Dropbox
        DropboxService = self.env['ir.config_parameter'].get_dropbox_service()
        folder_path = self.env['ir.config_parameter'].get_param("odoo_backup_sh_dropbox.dropbox_folder_path")
        info_file_size = info_file.tell()
        dump_stream.seek(0)
        info_file.seek(0)
        for obj, obj_name, file_size in \
                [[dump_stream, compute_backup_filename(name, ts, info_file_content.get('encrypted')), info_file_content.get("backup_size") * 1024 * 1024],
                 [info_file, compute_backup_info_filename(name, ts), info_file_size]]:
            # The full path to upload the file to, including the file name
            full_path = "{folder_path}/{file_name}".format(
                folder_path=folder_path,
                file_name=obj_name,
            )
            # from here: https://www.dropboxforum.com/t5/API-Support-Feedback/python-upload-big-file-example/m-p/166627/highlight/true#M6013
            if file_size <= CHUNK_SIZE:
                DropboxService.files_upload(obj.read(), full_path)
            else:
                upload_session_start_result = DropboxService.files_upload_session_start(obj.read(CHUNK_SIZE))
                cursor = UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=obj.tell())
                commit = CommitInfo(path=full_path)
                while obj.tell() < file_size:
                    if ((file_size - obj.tell()) <= CHUNK_SIZE):
                        DropboxService.files_upload_session_finish(obj.read(CHUNK_SIZE), cursor, commit)
                    else:
                        DropboxService.files_upload_session_append(obj.read(CHUNK_SIZE), cursor.session_id,
                                                                   cursor.offset)
                        cursor.offset = obj.tell()


class BackupInfo(models.Model):
    _inherit = 'odoo_backup_sh.backup_info'

    storage_service = fields.Selection(selection_add=[(DROPBOX_STORAGE, 'Dropbox')])

    def download_backup_action(self, backup=None):
        self.assert_user_can_download_backup()
        if backup is None:
            backup = get_backup_by_id(self.env, self._context['active_id'])

        if backup.storage_service != DROPBOX_STORAGE:
            return super(BackupInfo, self).download_backup_action(backup)

        # TODO: use backup_path field
        folder_path = self.env['ir.config_parameter'].get_param("odoo_backup_sh_dropbox.dropbox_folder_path") or ""
        DropboxService = self.env['ir.config_parameter'].get_dropbox_service()
        return {
            "type": "ir.actions.act_url",
            "url": DropboxService.files_get_temporary_link("{0}/{1}".format(folder_path, backup.backup_filename)).link,
            "target": "self",
        }


class BackupRemoteStorage(models.Model):
    _inherit = 'odoo_backup_sh.remote_storage'

    dropbox_used_remote_storage = fields.Integer(string='Dropbox Usage, MB', readonly=True)

    def compute_total_used_remote_storage(self):
        self.compute_dropbox_used_remote_storage()
        super(BackupRemoteStorage, self).compute_total_used_remote_storage()

    def compute_dropbox_used_remote_storage(self):
        amount = sum(self.env['odoo_backup_sh.backup_info'].search([('storage_service', '=', DROPBOX_STORAGE)]).mapped('backup_size'))
        today_record = self.search([('date', '=', datetime.strftime(datetime.now(), DEFAULT_SERVER_DATE_FORMAT))])
        if today_record:
            today_record.dropbox_used_remote_storage = amount
        else:
            self.create({
                'date': datetime.now(),
                'dropbox_used_remote_storage': amount
            })


class DeleteRemoteBackupWizard(models.TransientModel):
    _inherit = "odoo_backup_sh.delete_remote_backup_wizard"

    def delete_remove_backup_button(self):
        record_ids = []
        if self._context.get('active_model') == 'odoo_backup_sh.backup_info':
            record_ids = self._context.get('active_ids')

        backup_info_records = self.env['odoo_backup_sh.backup_info'].search([('id', 'in', record_ids)])
        folder_path = self.env['ir.config_parameter'].get_param("odoo_backup_sh_dropbox.dropbox_folder_path")
        DropboxService = self.env['ir.config_parameter'].get_dropbox_service()
        backup_dropbox_info_records = backup_info_records.filtered(lambda r: r.storage_service == DROPBOX_STORAGE)

        for record in backup_dropbox_info_records:
            for obj_name in [record.backup_filename, record.backup_info_filename]:
                full_path = "{folder_path}/{file_name}".format(
                    folder_path=folder_path,
                    file_name=obj_name,
                )
                DropboxService.files_delete(full_path)
        backup_dropbox_info_records.unlink()
        super(DeleteRemoteBackupWizard, self).delete_remove_backup_button()
