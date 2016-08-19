from openerp import api, models, fields, SUPERUSER_ID


class crm_lead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'reminder']
    _reminder_date_field = 'date_action'
    _reminder_description_field = 'title_action'
    reminder_alarm_ids = fields.Many2many(string='Next Action Reminders')
