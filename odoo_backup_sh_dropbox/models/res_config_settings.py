# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dropbox_access_token = fields.Char(string="Dropbox Access Token")
    dropbox_folder_path = fields.Char(string="Dropbox Folder Path", help="The Full Path to upload a Backup. E.g. /ProductionBackups")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("odoo_backup_sh_dropbox.dropbox_access_token", self.dropbox_access_token or '')
        ICPSudo.set_param("odoo_backup_sh_dropbox.dropbox_folder_path", self.dropbox_folder_path or '')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        dropbox_access_token = ICPSudo.get_param("odoo_backup_sh_dropbox.dropbox_access_token")
        dropbox_folder_path = ICPSudo.get_param("odoo_backup_sh_dropbox.dropbox_folder_path")
        res.update(
            dropbox_access_token=dropbox_access_token or False,
            dropbox_folder_path=dropbox_folder_path or False,
        )
        return res
