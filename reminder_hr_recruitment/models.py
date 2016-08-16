# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class HrApplicant(models.Model):
    _name = 'hr.applicant'
    _inherit = ['hr.applicant', 'reminder']
    _reminder_date_field = 'date_action'
    _reminder_description_field = 'title_action'
    reminder_alarm_ids = fields.Many2many(string='Next Action Reminders')
