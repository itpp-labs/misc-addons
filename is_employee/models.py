# -*- coding: utf-8 -*-
from openerp import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('user_ids')
    def _get_is_employee(self):
        self.is_employee = bool(self.user_ids.is_employee)

    is_employee = fields.Boolean('Is Employee', compute=_get_is_employee, store=True)

    @api.multi
    def _get_employee_id(self):
        for r in self:
            r._get_employee_id_one()
        return True

    @api.multi
    def _get_employee_id_one(self):
        self.ensure_one()
        self.employee_id = self.user_ids.employee_ids.ids and self.user_ids.employee_ids.ids[0] or None

    employee_id = fields.Many2one('hr.employee', string='Related employee', compute=_get_employee_id)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.one
    @api.depends('employee_ids')
    def _get_is_employee(self):
        self.is_employee = bool(self.employee_ids)

    is_employee = fields.Boolean('Is Employee', compute=_get_is_employee, store=True)
