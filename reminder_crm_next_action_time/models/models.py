# -*- coding: utf-8 -*-
from odoo import fields, models


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = ["crm.lead", "reminder"]
    date_action = fields.Datetime(string="Next Action Datetime")
    _reminder_date_field = "date_action"
    _reminder_description_field = "title_action"
    reminder_alarm_ids = fields.Many2many(string="Next Action Reminders")
