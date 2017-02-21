# -*- coding: utf-8 -*-
from odoo import fields, models, api


class BaseDetails(models.AbstractModel):
    """Model to be inherited by Model where details field has to be added"""
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
    details_model_exists = fields.Boolean(string='Details Model Exists')

    @api.onchange('details_model')
    def _onchange_details_model(self):
        if self.details_model and self.details_model in self.env:
            self.details_model_exists = True
        else:
            self.details_model_exists = False


class BaseDetailsRecord(models.AbstractModel):
    """Model to be inherited by Model with details"""

    _name = 'base_details_record'
    _base_details_model = 'UPDATE_THIS'

    @api.multi
    def _base_details_reversed(self):
        reversed_records = self.env[self._base_details_model].search_read([
            ('details_model', '=', self._name),
            ('details_res_id', 'in', self.ids),
        ], fields=['id', 'details_res_id'])
        return ((r['details_res_id'], r['id']) for r in reversed_records)
