from openerp import api,models,fields

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('user_ids')
    def _get_is_employee(self):
        self.is_employee = bool(self.user_ids.is_employee)

    is_employee = fields.Boolean('Is Employee', compute=_get_is_employee, store=True)

class res_users(models.Model):
    _inherit = 'res.users'

    @api.one
    @api.depends('employee_ids')
    def _get_is_employee(self):
        self.is_employee = bool(self.employee_ids)

    is_employee = fields.Boolean('Is Employee', compute=_get_is_employee, store=True)
