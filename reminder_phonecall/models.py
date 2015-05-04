from openerp import api, models, fields, SUPERUSER_ID


class crm_phonecall(models.Model):
    _name = 'crm.phonecall'
    _inherit = ['crm.phonecall', 'reminder']
    _reminder_date_field = 'date'
