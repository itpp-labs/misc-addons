from openerp import api,models,fields

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('user_ids')
    def _get_is_employee(self):
        self.is_employee = bool(self.user_ids.is_employee)

    is_employee = fields.Boolean('Is Employee', compute=_get_is_employee, store=True)

    @api.one
    def _get_employee_id(self):
        self.employee_id = self.user_ids.employee_ids.ids and self.user_ids.employee_ids.ids[0] or None

    employee_id = fields.Many2one('hr.employee', string='Related employee', compute=_get_employee_id)

class res_users(models.Model):
    _inherit = 'res.users'

    @api.one
    @api.depends('employee_ids')
    def _get_is_employee(self):
        self.is_employee = bool(self.employee_ids)

    is_employee = fields.Boolean('Is Employee', compute=_get_is_employee, store=True)
