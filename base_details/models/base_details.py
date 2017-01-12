# -*- coding: utf-8 -*-
from odoo import fields, models


class BaseDetails(models.AbstractModel):
    _name = 'base_details'

    def _model_selection(self):
        return []

    @property
    def details(self):
        if self.details_model and self.details_model in self.env and self.details_res_id:
            details_record = self.env[self.details_model].browse(self.details_res_id)
        else:
            details_record = None
        return details_record

    details_model = fields.Selection('_model_selection', string='Detail Model')
    details_res_id = fields.Integer(string='Details')
