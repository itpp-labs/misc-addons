# -*- coding: utf-8 -*-
from openerp import models


class Task(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'reminder']

    _reminder_date_field = 'date_deadline'
    _reminder_attendees_fields = ['user_id', 'reviewer_id']
