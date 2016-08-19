from openerp import api, models, fields


class res_users(models.Model):
    _inherit = 'res.users'

    company_default_id = fields.Many2one('res.company', string='Default company')
