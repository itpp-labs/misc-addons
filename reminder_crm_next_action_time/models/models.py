# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'reminder']
    datetime_action = fields.Datetime(string='Next Action Datetime')
    _reminder_date_field = 'datetime_action'
    _reminder_description_field = 'title_action'
    reminder_alarm_ids = fields.Many2many(string='Next Action Reminders')
