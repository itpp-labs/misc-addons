# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import copy
import logging
import os
import tempfile
from datetime import datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta

import odoo
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _

from ..controllers.main import (
    BACKUP_SERVICE_ENDPOINT,
    BackupCloudStorage,
    BackupController,
)

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

try:
    from pretty_bad_protocol import gnupg
except ImportError as err:
    logging.getLogger(__name__).debug(err)


config_parser = ConfigParser.ConfigParser()
_logger = logging.getLogger(__name__)

REMOTE_STORAGE_DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
BACKUP_NAME_SUFFIX = ".zip"
BACKUP_NAME_ENCRYPT_SUFFIX = BACKUP_NAME_SUFFIX + ".enc"
S3_STORAGE = "odoo_backup_sh"


def compute_backup_filename(database, upload_datetime, is_encrypted):
    return "{}.{}{}".format(
        database,
        datetime.strftime(upload_datetime, REMOTE_STORAGE_DATETIME_FORMAT)
        if type(upload_datetime) is not str
        else upload_datetime,
        BACKUP_NAME_ENCRYPT_SUFFIX if is_encrypted else BACKUP_NAME_SUFFIX,
    )


def compute_backup_info_filename(database, upload_datetime):
    return "{}.{}.info".format(
        database,
        datetime.strftime(upload_datetime, REMOTE_STORAGE_DATETIME_FORMAT)
        if type(upload_datetime) is not str
        else upload_datetime,
    )


def get_backup_by_id(env, backup_id):
    backup = env["odoo_backup_sh.backup_info"].browse(backup_id).exists()
    if len(backup) == 0:
        raise UserError(_("Backup not found: %s") % backup_id)
    return backup


class ModuleNotConfigured(Exception):
    pass


class BackupConfig(models.Model):
    _name = "odoo_backup_sh.config"
    _description = "Backup Configurations"
    _rec_name = "database"

    ROTATION_OPTIONS = [
        ("unlimited", "Unlimited"),
        ("limited", "Limited"),
        ("disabled", "Disabled"),
    ]

    active = fields.Boolean(
        "Active", compute="_compute_active", inverse="_inverse_active", store=True
    )

    @api.model
    def _compute_database_names(self):
        if odoo.tools.config["list_db"]:
            return [
                (db, db) for db in odoo.service.db.list_dbs() if db != "session_store"
            ]
        else:
            return [(self.env.cr.dbname, self.env.cr.dbname)]

    database = fields.Selection(
        selection=_compute_database_names, string="Database", required=True, copy=False
    )
    encrypt_backups = fields.Boolean(string="Encrypt Backups")
    encryption_password = fields.Char(string="Encryption Password")
    config_cron_ids = fields.One2many(
        "odoo_backup_sh.config.cron",
        "backup_config_id",
        string="Scheduled Auto Backups",
    )
    hourly_rotation = fields.Selection(
        selection=ROTATION_OPTIONS, string="Hourly", default="unlimited", required=True
    )
    daily_rotation = fields.Selection(
        selection=ROTATION_OPTIONS, string="Daily", default="unlimited", required=True
    )
    weekly_rotation = fields.Selection(
        selection=ROTATION_OPTIONS, string="Weekly", default="unlimited", required=True
    )
    monthly_rotation = fields.Selection(
        selection=ROTATION_OPTIONS, string="Monthly", default="unlimited", required=True
    )
    yearly_rotation = fields.Selection(
        selection=ROTATION_OPTIONS, string="Yearly", default="unlimited", required=True
    )
    hourly_limit = fields.Integer(
        "Hourly limit", default=1, help="How many hourly backups to preserve."
    )
    daily_limit = fields.Integer(
        "Daily limit", default=1, help="How many daily backups to preserve."
    )
    weekly_limit = fields.Integer(
        "Weekly limit", default=1, help="How many weekly backups to preserve."
    )
    monthly_limit = fields.Integer(
        "Monthly limit", default=1, help="How many monthly backups to preserve."
    )
    yearly_limit = fields.Integer(
        "Yearly limit", default=1, help="How many yearly backups to preserve."
    )
    storage_service = fields.Selection(
        selection=[(S3_STORAGE, "S3")], default=S3_STORAGE, required=True
    )
    unlimited_time_frame = fields.Char(default="hour")
    common_rotation = fields.Selection(selection=ROTATION_OPTIONS, default="unlimited")
    max_backups = fields.Integer(readonly=True, compute=lambda self: 0)
    backup_simulation = fields.Boolean(
        string="Demo Backup Simulation",
        default=False,
        help="If the setting is enabled then new backups of current database will not "
        "be sent to the storage server",
    )

    @api.model
    def _compute_backup_count(self):
        self.backup_count = len(
            self.env["odoo_backup_sh.backup_info"]
            .search([("database", "=", self.database)])
            ._ids
        )

    backup_count = fields.Integer("Backup count", compute=_compute_backup_count)

    _sql_constraints = [
        (
            "database_unique",
            "unique (database, storage_service)",
            "Settings for this database already exist!",
        ),
        (
            "hourly_limit_positive",
            "check (hourly_limit > 0)",
            "The hourly limit must be positive!",
        ),
        (
            "daily_limit_positive",
            "check (daily_limit > 0)",
            "The daily limit must be positive!",
        ),
        (
            "weekly_limit_positive",
            "check (weekly_limit > 0)",
            "The weekly limit must be positive!",
        ),
        (
            "monthly_limit_positive",
            "check (monthly_limit > 0)",
            "The monthly limit must be positive!",
        ),
        (
            "yearly_limit_positive",
            "check (yearly_limit > 0)",
            "The yearly limit must be positive!",
        ),
    ]

    @api.onchange(
        "config_cron_ids",
        "hourly_rotation",
        "daily_rotation",
        "weekly_rotation",
        "monthly_rotation",
        "yearly_rotation",
    )
    def _onchange_common_rotation(self):
        if self.config_cron_ids:
            rotation_list = [
                self.hourly_rotation,
                self.daily_rotation,
                self.weekly_rotation,
                self.monthly_rotation,
                self.yearly_rotation,
            ]
            if "unlimited" in rotation_list:
                self.common_rotation = "unlimited"
            elif "unlimited" not in rotation_list and "disabled" not in rotation_list:
                self.common_rotation = "limited"
            elif "unlimited" not in rotation_list and "limited" not in rotation_list:
                self.common_rotation = "disabled"
            else:
                self.common_rotation = "limited"
            self.set_unlimited_time_frame()
        else:
            self.common_rotation = None

    def set_unlimited_time_frame(self):
        if self.hourly_rotation == "unlimited":
            self.unlimited_time_frame = "hour"
        elif self.daily_rotation == "unlimited":
            self.unlimited_time_frame = "day"
        elif self.weekly_rotation == "unlimited":
            self.unlimited_time_frame = "week"
        elif self.monthly_rotation == "unlimited":
            self.unlimited_time_frame = "month"
        elif self.yearly_rotation == "unlimited":
            self.unlimited_time_frame = "year"
        else:
            self.unlimited_time_frame = None

    @api.onchange(
        "hourly_rotation",
        "hourly_limit",
        "daily_rotation",
        "daily_limit",
        "weekly_rotation",
        "weekly_limit",
        "monthly_rotation",
        "monthly_limit",
        "yearly_rotation",
        "yearly_limit",
    )
    def _onchange_max_backups(self):
        if self.common_rotation == "limited":
            max_backups = 0
            if self.hourly_rotation == "limited":
                max_backups += self.hourly_limit
            if self.daily_rotation == "limited":
                max_backups += self.daily_limit
            if self.weekly_rotation == "limited":
                max_backups += self.weekly_limit
            if self.monthly_rotation == "limited":
                max_backups += self.monthly_limit
            if self.yearly_rotation == "limited":
                max_backups += self.yearly_limit
            self.max_backups = max_backups

    @api.depends("config_cron_ids", "config_cron_ids.ir_cron_id.active")
    @api.multi
    def _compute_active(self):
        for backup_config in self:
            backup_config.active = backup_config.config_cron_ids and any(
                backup_config.config_cron_ids.mapped("active")
            )

    @api.multi
    def _inverse_active(self):
        for backup_config in self:
            backup_config.config_cron_ids.write({"active": backup_config.active})

    @api.multi
    def write(self, vals):
        if vals.get("common_rotation") == "disabled":
            raise UserError(
                _(
                    "You cannot save the settings where all rotation options are disabled."
                )
            )
        return super(BackupConfig, self).write(vals)

    @api.multi
    def unlink(self):
        self.mapped("config_cron_ids").unlink()
        return super(BackupConfig, self).unlink()

    @api.model
    def action_dashboard_redirect(self):
        return self.env.ref("odoo_backup_sh.backup_dashboard").read()[0]

    @api.model
    def get_cloud_params(self, redirect):
        return BackupController.get_cloud_params(redirect)

    def compute_auto_rotation_backup_dts(
        self, backup_dts, hourly=0, daily=0, weekly=0, monthly=0, yearly=0
    ):
        """
        returns lisf of datetimes that has to be kept
        """
        # TODO: it works too slow for hundreds of records
        backup_dts = sorted(backup_dts, reverse=True)
        last_backup_dt = backup_dts.pop(0)
        # We always take the last backup and based on its upload time we compute time frames
        # for other backups.
        needed_backup_dts = [last_backup_dt]
        if hourly > 1:
            last_backup_dt_of_hour = last_backup_dt
            for hour in range(hourly - 1):
                next_max_dt_edge = last_backup_dt_of_hour.replace(minute=0, second=0)
                for dt in backup_dts:
                    if dt < next_max_dt_edge:
                        needed_backup_dts.append(dt)
                        last_backup_dt_of_hour = dt
                        break
        if daily > 1:
            last_backup_dt_of_day = last_backup_dt
            for day in range(daily - 1):
                next_max_dt_edge = last_backup_dt_of_day.replace(
                    hour=0, minute=0, second=0
                )
                for dt in backup_dts:
                    if dt < next_max_dt_edge:
                        if dt not in needed_backup_dts:
                            needed_backup_dts.append(dt)
                        last_backup_dt_of_day = dt
                        break
        if weekly > 1:
            last_backup_dt_of_week = last_backup_dt
            for week in range(weekly - 1):
                last_backup_dt_day = last_backup_dt_of_week.replace(
                    hour=0, minute=0, second=0
                )
                next_max_dt_edge = last_backup_dt_day - timedelta(
                    days=last_backup_dt_day.weekday()
                )
                for dt in backup_dts:
                    if dt < next_max_dt_edge:
                        if dt not in needed_backup_dts:
                            needed_backup_dts.append(dt)
                        last_backup_dt_of_week = dt
                        break
        if monthly > 1:
            last_backup_dt_of_month = last_backup_dt
            for month in range(monthly - 1):
                next_max_dt_edge = last_backup_dt_of_month.replace(
                    day=1, hour=0, minute=0, second=0
                )
                for dt in backup_dts:
                    if dt < next_max_dt_edge:
                        if dt not in needed_backup_dts:
                            needed_backup_dts.append(dt)
                        last_backup_dt_of_month = dt
                        break
        if yearly > 1:
            last_backup_dt_of_year = last_backup_dt
            for year in range(yearly - 1):
                next_max_dt_edge = last_backup_dt_of_year.replace(
                    month=1, day=1, hour=0, minute=0, second=0
                )
                for dt in backup_dts:
                    if dt < next_max_dt_edge:
                        if dt not in needed_backup_dts:
                            needed_backup_dts.append(dt)
                        last_backup_dt_of_year = dt
                        break
        return needed_backup_dts

    @api.model
    def get_simulation_backup_list(self, config):
        info_records = self.env["odoo_backup_sh.backup_info"].search(
            [
                ("backup_simulation", "=", True),
                ("storage_service", "=", config.storage_service),
                ("database", "=", config.database),
            ]
        )
        simulation_backup_list = []
        for r in info_records:
            simulation_backup_list.append(
                (r.backup_info_filename, config.storage_service)
            )
            simulation_backup_list.append((r.backup_filename, config.storage_service))
        return simulation_backup_list

    @api.model
    def get_backup_list(self, cloud_params, service):
        if service != S3_STORAGE:
            return {}
        try:
            backup_list = BackupCloudStorage.get_all_files(cloud_params)
            # if the simulation configuration exists, we need to get
            # all the simulation info files and convert them to backup format
            configs = (
                self.env["odoo_backup_sh.config"]
                .with_context({"active_test": False})
                .search([("backup_simulation", "=", True)])
            )
            for config in configs:
                simulation_backup_list = self.get_simulation_backup_list(config)
                backup_list.update(
                    {"all_files": backup_list["all_files"] + simulation_backup_list}
                )
            return backup_list
        except Exception as e:
            _logger.exception("Failed to load backups")
            raise UserError(_("Failed to load backups: %s") % e)

    @api.model
    def get_info_file_object(self, cloud_params, info_file_name, storage_service):
        if storage_service == S3_STORAGE:
            return BackupCloudStorage.get_object(cloud_params, filename=info_file_name)

    @api.model
    def create_info_file(self, info_file_object, storage_service):
        if storage_service == S3_STORAGE:
            info_file = tempfile.NamedTemporaryFile()
            info_file.write(info_file_object["Body"].read())
            info_file.seek(0)
            return info_file

    @api.model
    def delete_remote_objects(self, cloud_params, remote_objects):
        odoo_backup_sh_objects = []
        path = None
        for obj in remote_objects:
            if obj[1] != S3_STORAGE:
                continue
            if not path:
                path = BackupCloudStorage.get_s3_dir(cloud_params)
            odoo_backup_sh_objects.append("{}/{}".format(path, obj[0]))
        if odoo_backup_sh_objects:
            return BackupCloudStorage.delete_objects(
                cloud_params, odoo_backup_sh_objects
            )
        return {}

    @api.model
    def update_info(self, cloud_params, service=None):
        """
        * apply rotations
        * sync odoo_backup_sh.backup_info records:

          * create missed records for found backups in the remote storage
          * archive existed records that don't have corresponding backup in the remote storage
        """
        backup_list = self.get_backup_list(cloud_params, service)
        if not backup_list.get("all_files"):
            return backup_list

        # Create a dictionary with remote backup objects:
        # remote_backups = {
        #     db_name: {
        #         backup_datetime::datetime.datetime: [(file_name::str, service_name::str)],
        #         ...
        #     },
        #     ...
        # }
        remote_backups = {}
        for f in backup_list["all_files"]:
            # file_name has on of follogin format:
            # DATABASE_NAME.TIMESTAMP_WITHOUT_DOTES.zip[.enc]
            # DATABASE_NAME.TIMESTAMP_WITHOUT_DOTES.info
            # see compute_backup_filename, compute_backup_info_filename
            file_name = f[0]
            # service_name is odoo_backup_sh, dropbox, etc.
            service_name = f[1]
            file_name_parts = file_name.split(".")
            try:
                if file_name_parts[-1] == "enc":
                    file_name_parts = file_name_parts[:-1]
                timestamp = file_name_parts[-2]
                db_name = ".".join(file_name_parts[:-2])
                backup_dt = datetime.strptime(timestamp, REMOTE_STORAGE_DATETIME_FORMAT)
            except (IndexError, ValueError):
                _logger.warning("Cannot parse file name: %s", file_name)
                continue
            remote_backups.setdefault(db_name, {})
            remote_backups[db_name].setdefault(backup_dt, [])
            remote_backups[db_name][backup_dt].append((file_name, service_name))
        _logger.debug("remote_backups: %s", remote_backups)

        # Compute remote backup objects to delete according to auto rotation parameters.
        remote_objects_to_delete = []
        remote_objects_to_archive = []
        for backup_config in self.search([("active", "=", True)]):
            limits = {}
            for time_frame in ("hourly", "daily", "weekly", "monthly", "yearly"):
                limit_option = getattr(backup_config, time_frame + "_rotation")
                if limit_option == "limited":
                    limits[time_frame] = getattr(backup_config, time_frame + "_limit")
                elif limit_option == "unlimited":
                    limits[time_frame] = 1000000
                    # we don't need to have some extra backups for futher periods
                    break
            if not limits:
                # no rotations rules
                continue
            remote_db = remote_backups.get(backup_config.database, False)
            if not remote_db:
                continue

            # filter current dict by service name

            # TODO: this works only in assumption that there are no backups
            # made in same second for different storages. Otherwise we need
            # to check storage service in each tuple of remote_db[dt] array
            remote_db_filtered = {}
            for dt in remote_db:
                if len(remote_db[dt]) != 2:
                    continue
                if remote_db[dt][0][1] != backup_config.storage_service:
                    continue
                remote_db_filtered[dt] = remote_db[dt]

            remote_db = remote_db_filtered
            if not remote_db:
                continue
            backup_dts = copy.deepcopy(remote_db)
            needed_backup_dts = self.compute_auto_rotation_backup_dts(
                backup_dts.keys(), **limits
            )
            for backup_dt in backup_dts:
                if backup_dt in needed_backup_dts:
                    continue
                if backup_config.backup_simulation is False:
                    remote_objects_to_delete += remote_backups[backup_config.database][
                        backup_dt
                    ]
                remote_objects_to_archive += remote_backups[backup_config.database][
                    backup_dt
                ]
                del remote_backups[backup_config.database][backup_dt]

        _logger.debug("remote_objects_to_delete: %s", remote_objects_to_delete)
        # Delete unnecessary remote backup objects
        if remote_objects_to_delete:
            res = self.delete_remote_objects(cloud_params, remote_objects_to_delete)
            if res and "reload_page" in res:
                return res

        # Archive unnecessary local backup info records
        backup_info_ids_to_archive = []
        # TODO: it would work slow if we have hundreds of backups
        for r in self.env["odoo_backup_sh.backup_info"].search([("active", "=", True)]):
            obj = (r.backup_filename, r.storage_service)
            if obj not in backup_list["all_files"] or obj in remote_objects_to_archive:
                backup_info_ids_to_archive.append(r.id)
        _logger.debug("backup_info_ids_to_archive: %s", backup_info_ids_to_archive)

        # Archive old records
        self.env["odoo_backup_sh.backup_info"].browse(backup_info_ids_to_archive).write(
            {"active": False}
        )
        # Compute total remote storage after archive
        self.env["odoo_backup_sh.remote_storage"].compute_total_used_remote_storage()

        # Create missing local backup info records
        for db_name, backup_dts in remote_backups.items():
            for backup_dt, files in backup_dts.items():
                # TODO: use backup_filename field to search for record
                # TODO: this works only in assumption that there are no backups
                # made in same second for different storages.
                record_exists = self.env["odoo_backup_sh.backup_info"].search(
                    [
                        ("database", "=", db_name),
                        (
                            "upload_datetime",
                            ">=",
                            datetime.strftime(
                                backup_dt, DEFAULT_SERVER_DATETIME_FORMAT
                            ),
                        ),
                        (
                            "upload_datetime",
                            "<",
                            datetime.strftime(
                                backup_dt + relativedelta(seconds=1),
                                DEFAULT_SERVER_DATETIME_FORMAT,
                            ),
                        ),
                    ]
                )
                if record_exists:
                    continue
                if len(files) != 2:
                    _logger.warning("Not a pair of files found: %s", files)
                    continue
                info_file = files[0] if files[0][0][-5:] == ".info" else files[1]
                if not info_file:
                    continue
                info_file_name = info_file[0]
                info_file_service = info_file[1]
                info_file_object = self.get_info_file_object(
                    cloud_params, info_file_name, info_file_service
                )

                if "reload_page" in info_file_object:
                    return info_file_object
                info_file = self.create_info_file(info_file_object, info_file_service)
                config_parser.read(info_file.name)
                backup_info_vals = {}

                # TODO: call a method, that will compute path depending on storage
                if info_file_service == S3_STORAGE:
                    backup_info_vals["backup_path"] = BackupCloudStorage.get_s3_dir(
                        cloud_params
                    )
                for (name, value) in config_parser.items("common"):
                    if value == "True" or value == "true":
                        value = True
                    if value == "False" or value == "false":
                        value = False
                    if name == "upload_datetime":
                        value = datetime.strptime(value, REMOTE_STORAGE_DATETIME_FORMAT)
                    elif name == "backup_size":
                        value = int(float(value))
                    backup_info_vals[name] = value
                self.env["odoo_backup_sh.backup_info"].create(backup_info_vals)
        return backup_list

    @api.model
    def get_dump_stream_and_info_file(self, name, service, ts):
        config_record = self.with_context({"active_test": False}).search(
            [("database", "=", name), ("storage_service", "=", service)]
        )
        if config_record.backup_simulation:
            dump_stream = tempfile.TemporaryFile()
        else:
            dump_stream = odoo.service.db.dump_db(name, None, "zip")

        if config_record.encrypt_backups and config_record.backup_simulation is False:
            # GnuPG ignores the --output parameter with an existing file object as value
            backup_encrpyted = tempfile.NamedTemporaryFile()
            backup_encrpyted_name = backup_encrpyted.name
            os.unlink(backup_encrpyted_name)
            gnupg.GPG().encrypt(
                dump_stream,
                symmetric=True,
                passphrase=config_record.encryption_password,
                encrypt=False,
                output=backup_encrpyted_name,
            )
            dump_stream = open(backup_encrpyted_name, "rb")

        # simulation backup size is 1 MB
        backup_size = (
            dump_stream.seek(0, 2) / 1024 / 1024
            if config_record.backup_simulation is False
            else 1
        )
        dump_stream.seek(0)
        info_file = tempfile.TemporaryFile()
        info_file.write(b"[common]\n")
        info_file_content = {
            "database": name,
            "encrypted": True if config_record.encrypt_backups else False,
            "upload_datetime": ts,
            "backup_size": backup_size,
            "storage_service": config_record.storage_service,
        }
        for key, value in info_file_content.items():
            line = key + " = " + str(value) + "\n"
            info_file.write(line.encode())
        info_file.seek(0)
        return dump_stream, info_file, info_file_content

    @api.model
    def make_backup(self, name, service, init_by_cron_id=None):
        if init_by_cron_id and not self.env["ir.cron"].browse(init_by_cron_id).active:
            # The case when an auto backup was initiated by an inactive backup config.
            return None

        config_record = self.with_context({"active_test": False}).search(
            [("database", "=", name), ("storage_service", "=", service)]
        )
        if not config_record:
            return None

        cloud_params = None
        # TODO: cloud_params is in fact s3 params only. So, method should be
        # refactored to don't use cloud_params, because dropbox and google
        # drive modules don't use them
        if service == S3_STORAGE:
            cloud_params = BackupController.get_cloud_params(env=self.env)
        dt = datetime.utcnow()
        ts = dt.strftime(REMOTE_STORAGE_DATETIME_FORMAT)
        dump_stream, info_file, info_file_content = self.get_dump_stream_and_info_file(
            name, service, ts
        )
        dump_stream.seek(0)
        info_file.seek(0)
        cust_method_name = "make_backup_%s" % service
        # make a backup if it is not a simulation
        if hasattr(self, cust_method_name) and config_record.backup_simulation is False:
            method = getattr(self, cust_method_name)
            method(ts, name, dump_stream, info_file, info_file_content, cloud_params)

        # Create new record with backup info data
        info_file_content["upload_datetime"] = dt
        self.env["odoo_backup_sh.backup_info"].sudo().create(info_file_content)
        if init_by_cron_id:
            self.update_info(cloud_params, service=service)
        return None

    @api.model
    def make_backup_odoo_backup_sh(
        self, ts, name, dump_stream, info_file, info_file_content, cloud_params
    ):
        s3_backup_name = compute_backup_filename(
            name, ts, info_file_content.get("encrypted")
        )
        s3_info_file_name = compute_backup_info_filename(name, ts)
        # Upload two backup objects to AWS S3
        for obj, obj_name in [
            (dump_stream, s3_backup_name),
            (info_file, s3_info_file_name),
        ]:
            try:
                path = BackupCloudStorage.get_s3_dir(cloud_params)
                obj_key = "{}/{}".format(path, obj_name)
                info_file_content["backup_path"] = path
                res = BackupCloudStorage.put_object(cloud_params, obj, obj_key)
                if res and "reload_page" in res:
                    return res
            except Exception as e:
                _logger.exception("Failed to create backup")
                raise UserError(_("Failed to create backup: %s") % e)

    @api.multi
    def action_create_simulation_data(self):
        self.install_demo_data()
        return True

    @api.model
    def install_simulation(self):
        # when installing with demo data we create new simulation backup config (for creating simulation records)
        vals = {
            "database": self._cr.dbname,
            "encrypt_backups": False,
            "storage_service": S3_STORAGE,
            "backup_simulation": True,
        }
        domain = [(k, "=", v) for k, v in vals.items()]
        if self.with_context(active_test=False).search(domain):
            # Already initialized

            # Seems that this check is needed in odoo 11, cause in odoo 12
            # <function> in demo is called only on module installation
            return
        config = self.create(vals)
        config.install_demo_data()

    @api.multi
    def install_demo_data(self):
        # create lot of backup info files (fake backups)
        info_obj = self.env["odoo_backup_sh.backup_info"]
        number_of_backups = 1000
        upload_datetime = datetime.now()
        for index in range(number_of_backups):
            info_obj.create(
                {
                    "database": self.database,
                    "upload_datetime": upload_datetime,
                    "encrypted": False,
                    "backup_size": 1,
                    "storage_service": self.storage_service,
                    "backup_simulation": self.backup_simulation,
                }
            )
            upload_datetime -= relativedelta(hours=4)

    @api.multi
    def action_list_backups(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Backup list",
            "view_mode": "tree,form,pivot,graph,activity",
            "res_model": "odoo_backup_sh.backup_info",
            "domain": [("database", "=", self.database)],
            "search_view_id": self.env.ref(
                "odoo_backup_sh.odoo_backup_sh_backup_search"
            ).id,
        }


class BackupConfigCron(models.Model):
    _name = "odoo_backup_sh.config.cron"
    _inherits = {"ir.cron": "ir_cron_id"}
    _description = "Backup Configuration Scheduled Actions"

    backup_config_id = fields.Many2one(
        "odoo_backup_sh.config", string="Backup Configuration", required=True
    )
    ir_cron_id = fields.Many2one(
        "ir.cron", string="Scheduled Action", required=True, ondelete="restrict"
    )

    @api.model
    def create(self, vals):
        config = self.env["odoo_backup_sh.config"].browse(vals["backup_config_id"])
        vals.update(
            {
                "name": 'Odoo-backup.sh: Backup the "%s" database, send it to %s storage, apply rotation'
                % (config.database, config.storage_service),
                "model_id": self.env.ref(
                    "odoo_backup_sh.model_odoo_backup_sh_config"
                ).id,
                "state": "code",
                "numbercall": -1,
                "doall": False,
            }
        )
        res = super(BackupConfigCron, self).create(vals)
        res.write(
            {
                "code": 'model.make_backup("%s", "%s", init_by_cron_id=%s)'
                % (config.database, config.storage_service, res.ir_cron_id.id)
            }
        )
        return res

    @api.multi
    def unlink(self):
        ir_cron_ids = [r.ir_cron_id.id for r in self]
        res = super(BackupConfigCron, self).unlink()
        if ir_cron_ids:
            self.env["ir.cron"].browse(ir_cron_ids).unlink()
        return res


class BackupInfo(models.Model):
    _name = "odoo_backup_sh.backup_info"
    _description = "Information About Backups"
    _rec_name = "database"

    database = fields.Char(string="Database Name", readonly=True)
    upload_datetime = fields.Datetime(string="Upload Datetime", readonly=True)
    encrypted = fields.Boolean(string="Encrypted", readonly=True)
    backup_size = fields.Float(string="Backup Size, MB", readonly=True)
    storage_service = fields.Selection(selection=[(S3_STORAGE, "S3")], readonly=True)
    backup_simulation = fields.Boolean(
        default=False,
        readonly=True,
        help="If this option is enabled, the backup information will not be deleted "
        "after updating the backup list.",
    )
    active = fields.Boolean(
        "Active",
        default=True,
        readonly=True,
        help="Non-active record means that the backup file was deleted",
    )

    def _compute_backup_filename(self):
        for r in self:
            r.backup_filename = compute_backup_filename(
                r.database,
                datetime.strptime(r.upload_datetime, DEFAULT_SERVER_DATETIME_FORMAT),
                r.encrypted,
            )

    def _compute_backup_info_filename(self):
        for r in self:
            r.backup_info_filename = compute_backup_info_filename(
                r.database,
                datetime.strptime(r.upload_datetime, DEFAULT_SERVER_DATETIME_FORMAT),
            )

    backup_path = fields.Char()
    # TODO: Shall we make those fields static?
    backup_filename = fields.Char(compute=_compute_backup_filename, store=False)
    backup_info_filename = fields.Char(
        compute=_compute_backup_info_filename, store=False
    )

    @api.model
    def create(self, vals):
        res = super(BackupInfo, self).create(vals)
        self.env["odoo_backup_sh.remote_storage"].compute_total_used_remote_storage()
        return res

    @api.multi
    def unlink(self):
        res = super(BackupInfo, self).unlink()
        self.env["odoo_backup_sh.remote_storage"].compute_total_used_remote_storage()
        return res

    def assert_user_can_download_backup(self):
        if not self.user_has_groups("odoo_backup_sh.group_manager"):
            raise AccessError(_("Current user is not in Backup manager group"))

    @api.multi
    def download_backup_action(self, backup=None):
        self.assert_user_can_download_backup()

        if backup is not None:
            if backup.storage_service != S3_STORAGE:
                raise UserError(
                    _("Unknown storage service: %s") % backup.storage_service
                )
            backup_id = backup.id
        else:
            backup_id = self._context["active_id"]

        return {
            "type": "ir.actions.act_url",
            "url": "/web/database/backup?backup_id={}".format(backup_id),
            "target": "self",
        }


class BackupNotification(models.Model):
    _name = "odoo_backup_sh.notification"
    _description = "Backup Notifications"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_create desc"
    _rec_name = "date_create"

    date_create = fields.Datetime("Date", readonly=True, default=fields.Datetime.now)
    type = fields.Selection(
        [
            ("insufficient_credits", "Insufficient Credits"),
            ("forecast_insufficient_credits", "Forecast About Insufficient Credits"),
            ("other", "Other"),
        ],
        string="Notification Type",
        readonly=True,
        default="other",
    )
    message = fields.Text("Message", readonly=True)
    is_read = fields.Boolean("Is Read", readonly=True)

    @api.multi
    def toggle_is_read(self):
        self.write({"is_read": not self.is_read})
        self.activity_ids.unlink()
        return True

    @api.multi
    def create_mail_activity_record(self):
        self.env["mail.activity"].create(
            {
                "res_id": self.id,
                "res_model_id": self.env.ref(
                    "odoo_backup_sh.model_odoo_backup_sh_notification"
                ).id,
                "activity_type_id": self.env.ref(
                    "odoo_backup_sh.mail_activity_data_notification"
                ).id,
                "summary": "Please read important message.",
                "date_deadline": datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
            }
        )

    @api.model
    def fetch_notifications(self):
        config_params = self.env["ir.config_parameter"]
        data = {
            "params": {
                "user_key": config_params.get_param("odoo_backup_sh.user_key"),
                "date_last_request": config_params.get_param(
                    "odoo_backup_sh.date_last_request", None
                ),
            }
        }
        response = requests.post(
            BACKUP_SERVICE_ENDPOINT + "/fetch_notifications", json=data
        ).json()["result"]
        config_params.set_param(
            "odoo_backup_sh.date_last_request", response["date_last_request"]
        )
        for n in response["notifications"]:
            if n.get("type") == "forecast_insufficient_credits":
                existing_forecast_msg = self.search(
                    [("type", "=", "forecast_insufficient_credits")]
                )
                if existing_forecast_msg:
                    if existing_forecast_msg.activity_ids:
                        existing_forecast_msg.activity_ids.unlink()
                    existing_forecast_msg.unlink()
            new_record = self.create(n)
            new_record.create_mail_activity_record()


class BackupRemoteStorage(models.Model):
    _name = "odoo_backup_sh.remote_storage"
    _description = "Remote Storage Usage"

    date = fields.Date(string="Date of Update", readonly=True)
    total_used_remote_storage = fields.Integer(string="Total Usage, MB", readonly=True)
    s3_used_remote_storage = fields.Integer(
        string="Odoo Backup sh Usage, MB", readonly=True
    )

    @api.multi
    def compute_total_used_remote_storage(self):
        _logger.debug("compute_total_used_remote_storage...")
        self.compute_s3_used_remote_storage()
        amount = sum(
            self.env["odoo_backup_sh.backup_info"].search([]).mapped("backup_size")
        )
        _logger.debug("compute_total_used_remote_storage: %s", amount)
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
            today_record.total_used_remote_storage = amount
        else:
            self.create({"date": datetime.now(), "total_used_remote_storage": amount})

    @api.multi
    def compute_s3_used_remote_storage(self):
        amount = sum(
            self.env["odoo_backup_sh.backup_info"]
            .search([("storage_service", "=", S3_STORAGE)])
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
            today_record.s3_used_remote_storage = amount
        else:
            self.create({"date": datetime.now(), "s3_used_remote_storage": amount})


class DeleteRemoteBackupWizard(models.TransientModel):
    _name = "odoo_backup_sh.delete_remote_backup_wizard"
    _description = "Delete Remote Backups Wizard"

    @api.multi
    def delete_remove_backup_button(self):
        record_ids = []
        if self._context.get("active_model") == "odoo_backup_sh.backup_info":
            record_ids = self._context.get("active_ids")

        backup_info_records = self.env["odoo_backup_sh.backup_info"].search(
            [("id", "in", record_ids)]
        )
        cloud_params = BackupController.get_cloud_params()
        remote_objects_to_delete = []
        backup_s3_info_records = backup_info_records.filtered(
            lambda r: r.storage_service == S3_STORAGE
        )

        for record in backup_s3_info_records:
            for path, filename in [
                (record.backup_path, record.backup_filename),
                (record.backup_path, record.backup_info_filename),
            ]:
                remote_objects_to_delete.append("{}/{}".format(path, filename))

        # Delete unnecessary remote backup objects
        if remote_objects_to_delete:
            res = BackupCloudStorage.delete_objects(
                cloud_params, remote_objects_to_delete
            )
            if res and "reload_page" in res:
                raise UserError(
                    _("Something went wrong. Please update backup dashboard page.")
                )
        backup_s3_info_records.unlink()
