from openerp import api,models,fields
from openerp.osv import fields as old_fields

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    default_section_id = fields.Many2one('crm.case.section', 'Default Sales Team', related='user_id.default_section_id')

    personal_comission = fields.Float('Personal comission', help='Personal comission for sales. Value 1.0 is equal 1%')

    team_bonus = fields.Float('Team bonus', help='Maximum team bonus (per year). Value 1.0 is equal 1%')

    company_bonus = fields.Float('Company bonus', help='Maximum team bonus (per year). Value 1.0 is equal 1%')
