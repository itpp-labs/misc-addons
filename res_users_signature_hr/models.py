# -*- coding: utf-8 -*-
from openerp import api
from openerp import models


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def write(self, vals):
        res = super(hr_employee, self).write(vals)
        self.user_id.render_signature_id()
        return res
