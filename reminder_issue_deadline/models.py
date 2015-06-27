from openerp import models


class task(models.Model):
    _name = 'project.issue'
    _inherit = ['project.issue', 'reminder']

    _reminder_date_field = 'date_deadline'
    _reminder_attendees_fields = ['user_id']
