from odoo import models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def is_admin(self):
        # By default Python functions starting with _ are considered private methods.
        # Private methods (such as _is_admin) cannot be called remotely
        return self._is_admin()
