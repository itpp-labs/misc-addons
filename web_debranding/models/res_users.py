# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.multi
    def is_admin(self):
        # By default Python functions starting with _ are considered private methods.
        # Private methods (such as _is_admin) cannot be called remotely
        return self._is_admin()
