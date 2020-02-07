# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import io
import logging
import tempfile
from datetime import datetime

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo.addons.odoo_backup_sh.models.odoo_backup_sh import (
    ModuleNotConfigured,
    compute_backup_filename,
    compute_backup_info_filename,
    get_backup_by_id,
)

try:
    from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
    from apiclient import errors
except ImportError as err:
    logging.getLogger(__name__).debug(err)


_logger = logging.getLogger(__name__)
GOOGLE_DRIVE_STORAGE = "google_drive"


class BackupConfig(models.Model):
    _inherit = "odoo_backup_sh.config"

    storage_service = fields.Selection(
        selection_add=[(GOOGLE_DRIVE_STORAGE, "Google Drive")]
    )

    @api.model
    def get_backup_list(self, cloud_params, service):
        backup_list = (
            super(BackupConfig, self).get_backup_list(cloud_params, service) or dict()
        )
        if service != GOOGLE_DRIVE_STORAGE:
            return backup_list

        # get all backups from Google Drive
        try:
            GoogleDriveService = self.env[
                "ir.config_parameter"
            ].get_google_drive_service()
        except ModuleNotConfigured:
            return backup_list
        folder_id = self.env["ir.config_parameter"].get_param(
            "odoo_backup_sh_google_disk.google_disk_folder_id"
        )
        response = (
            GoogleDriveService.files()
            .list(
                q="'" + folder_id + "' in parents",
                fields="nextPageToken, files(id, name)",
                spaces="drive",
            )
            .execute()
        )
        google_drive_backup_list = [
            (r.get("name"), GOOGLE_DRIVE_STORAGE) for r in response.get("files", [])
        ]
        if "all_files" in backup_list:
            backup_list.update(
                {"all_files": backup_list["all_files"] + google_drive_backup_list}
            )
        else:
            backup_list["all_files"] = google_drive_backup_list
        return backup_list

    @api.model
    def get_info_file_object(self, cloud_params, info_file_name, storage_service):
        if storage_service == GOOGLE_DRIVE_STORAGE:
            GoogleDriveService = self.env[
                "ir.config_parameter"
            ].get_google_drive_service()
            file_id = self.get_google_drive_file_id(info_file_name)
            if file_id:
                fh = io.BytesIO()
                request = GoogleDriveService.files().get_media(fileId=file_id)
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                fh.seek(0)
                return fh
        else:
            return super(BackupConfig, self).get_info_file_object(
                cloud_params, info_file_name, storage_service
            )

    @api.model
    def get_google_drive_file_id(self, file_name):
        GoogleDriveService = self.env["ir.config_parameter"].get_google_drive_service()
        folder_id = self.env["ir.config_parameter"].get_param(
            "odoo_backup_sh_google_disk.google_disk_folder_id"
        )
        response = (
            GoogleDriveService.files()
            .list(
                q="'" + folder_id + "' in parents and name = '" + file_name + "'",
                fields="nextPageToken, files(id)",
                spaces="drive",
            )
            .execute()
        )
        file = response.get("files", [])
        return file[0].get("id")

    @api.model
    def create_info_file(self, info_file_object, storage_service):
        if storage_service == GOOGLE_DRIVE_STORAGE:
            info_file_object.seek(0)
            info_file = tempfile.NamedTemporaryFile()
            info_file.write(info_file_object.read())
            info_file.seek(0)
            return info_file
        else:
            return super(BackupConfig, self).create_info_file(
                info_file_object, storage_service
            )

    @api.model
    def delete_remote_objects(self, cloud_params, remote_objects):
        GoogleDriveService = None
        google_drive_remove_objects = []
        for file in remote_objects:
            if file[1] == GOOGLE_DRIVE_STORAGE:
                if not GoogleDriveService:
                    GoogleDriveService = self.env[
                        "ir.config_parameter"
                    ].get_google_drive_service()
                google_drive_remove_objects.append(file)
                file_id = self.get_google_drive_file_id(file[0])
                try:
                    GoogleDriveService.files().delete(fileId=file_id).execute()
                except errors.HttpError as e:
                    _logger.exception(e)
        return super(BackupConfig, self).delete_remote_objects(
            cloud_params, list(set(remote_objects) - set(google_drive_remove_objects))
        )

    @api.model
    def make_backup_google_drive(
        self, ts, name, dump_stream, info_file, info_file_content, cloud_params
    ):
        # Upload two backup objects to Google Drive
        GoogleDriveService = self.env["ir.config_parameter"].get_google_drive_service()
        folder_id = self.env["ir.config_parameter"].get_param(
            "odoo_backup_sh_google_disk.google_disk_folder_id"
        )
        db_metadata = {
            "name": compute_backup_filename(
                name, ts, info_file_content.get("encrypted")
            ),
            "parents": [folder_id],
        }
        info_metadata = {
            "name": compute_backup_info_filename(name, ts),
            "parents": [folder_id],
        }
        db_mimetype = "application/zip"
        info_mimetype = "text/plain"
        dump_stream.seek(0)
        info_file.seek(0)
        for obj, mimetype, metadata in [
            [dump_stream, db_mimetype, db_metadata],
            [info_file, info_mimetype, info_metadata],
        ]:
            media = MediaIoBaseUpload(obj, mimetype, resumable=True)
            GoogleDriveService.files().create(
                body=metadata, media_body=media, fields="id"
            ).execute()


class BackupInfo(models.Model):
    _inherit = "odoo_backup_sh.backup_info"

    storage_service = fields.Selection(
        selection_add=[(GOOGLE_DRIVE_STORAGE, "Google Drive")]
    )

    def download_backup_action(self, backup=None):
        self.assert_user_can_download_backup()

        if backup is None:
            backup = get_backup_by_id(self.env, self._context["active_id"])

        if backup.storage_service != GOOGLE_DRIVE_STORAGE:
            return super(BackupInfo, self).download_backup_action(backup)

        # TODO: add file_id in backup_info for this
        file_id = self.env["odoo_backup_sh.config"].get_google_drive_file_id(
            backup.backup_filename
        )
        return {
            "type": "ir.actions.act_url",
            "url": "https://drive.google.com/uc?id={}&export=download".format(file_id),
            "target": "self",
        }


class BackupRemoteStorage(models.Model):
    _inherit = "odoo_backup_sh.remote_storage"

    google_drive_used_remote_storage = fields.Integer(
        string="Google Drive Usage, MB", readonly=True
    )

    def compute_total_used_remote_storage(self):
        self.compute_google_drive_used_remote_storage()
        super(BackupRemoteStorage, self).compute_total_used_remote_storage()

    def compute_google_drive_used_remote_storage(self):
        amount = sum(
            self.env["odoo_backup_sh.backup_info"]
            .search([("storage_service", "=", GOOGLE_DRIVE_STORAGE)])
            .mapped("backup_size")
        )
        today_record = self.search(
            [
                (
                    "date",
                    "=",
                    datetime.strftime(datetime.now(), DEFAULT_SERVER_DATE_FORMAT),
                )
            ]
        )
        if today_record:
            today_record.google_drive_used_remote_storage = amount
        else:
            self.create(
                {"date": datetime.now(), "google_drive_used_remote_storage": amount}
            )


class DeleteRemoteBackupWizard(models.TransientModel):
    _inherit = "odoo_backup_sh.delete_remote_backup_wizard"

    def delete_remove_backup_button(self):
        record_ids = []
        if self._context.get("active_model") == "odoo_backup_sh.backup_info":
            record_ids = self._context.get("active_ids")

        backup_info_records = self.env["odoo_backup_sh.backup_info"].search(
            [("id", "in", record_ids)]
        )
        GoogleDriveService = self.env["ir.config_parameter"].get_google_drive_service()
        backup_google_drive_info_records = backup_info_records.filtered(
            lambda r: r.storage_service == GOOGLE_DRIVE_STORAGE
        )
        for record in backup_google_drive_info_records:
            for obj_name in [record.backup_filename, record.backup_info_filename]:
                file_id = self.env["odoo_backup_sh.config"].get_google_drive_file_id(
                    obj_name
                )
                try:
                    GoogleDriveService.files().delete(fileId=file_id).execute()
                except errors.HttpError as e:
                    _logger.exception(e)
        backup_google_drive_info_records.unlink()
        super(DeleteRemoteBackupWizard, self).delete_remove_backup_button()
