# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import api, models

from odoo.addons.odoo_backup_sh.models.odoo_backup_sh import ModuleNotConfigured

_logger = logging.getLogger(__name__)

try:
    import dropbox
except ImportError as err:
    _logger.debug(err)


class Param(models.Model):

    _inherit = "ir.config_parameter"

    @api.model
    def get_dropbox_service(self):
        dropbox_access_token = self.sudo().get_param(
            "odoo_backup_sh_dropbox.dropbox_access_token"
        )
        if not dropbox_access_token:
            raise ModuleNotConfigured("no access token given for dropbox")
        return dropbox.Dropbox(dropbox_access_token)
