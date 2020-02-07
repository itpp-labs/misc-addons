# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import json
import logging

from odoo import api, models
from odoo.addons.odoo_backup_sh.models.odoo_backup_sh import \
    ModuleNotConfigured

_logger = logging.getLogger(__name__)

try:
    from google.oauth2 import service_account
except ImportError as err:
    _logger.debug(err)

try:
    from googleapiclient.discovery import build
    from googleapiclient.discovery_cache.base import Cache
except ImportError as err:
    Cache = object
    _logger.debug(err)

# all scopes you can find: here https://developers.google.com/identity/protocols/googlescopes
SCOPES = ["https://www.googleapis.com/auth/drive"]


# https://stackoverflow.com/questions/15783783/python-import-error-no-module-named-appengine-ext
class MemoryCache(Cache):
    _CACHE = {}

    def get(self, url):
        return MemoryCache._CACHE.get(url)

    def set(self, url, content):
        MemoryCache._CACHE[url] = content


class Param(models.Model):

    _inherit = "ir.config_parameter"

    @api.model
    def get_google_drive_service(self):
        service_account_key = self.sudo().get_param(
            "odoo_backup_sh_google_disk.service_account_key"
        )
        if not service_account_key:
            raise ModuleNotConfigured("service account key is not set")
        try:
            service_account_key = json.loads(service_account_key.strip())
        except json.JSONDecodeError:
            raise ModuleNotConfigured("Service Key value is not a json")
        # create a credentials
        credentials = service_account.Credentials.from_service_account_info(
            service_account_key, scopes=SCOPES
        )
        # create a service using REST API Google Drive v3 and credentials
        service = build("drive", "v3", credentials=credentials, cache=MemoryCache())
        return service
