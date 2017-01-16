# -*- coding: utf-8 -*-
from openerp import api
from openerp import models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def write(self, vals):
        for r in self:
            r.write_one(self, vals)
        return True

    @api.multi
    def write_one(self, vals):
        self.ensure_one()
        res = super(HrEmployee, self).write(vals)
        self.user_id.render_signature_id()
        return res
