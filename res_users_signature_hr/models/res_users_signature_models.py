# Copyright 2014 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        for r in self:
            r.user_id.render_signature_id()
        return res
