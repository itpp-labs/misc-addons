from openerp import api, models, fields, SUPERUSER_ID


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def write(self, vals):
        res = super(hr_employee, self).write(vals)
        self.user_id.render_signature_id()
        return res
