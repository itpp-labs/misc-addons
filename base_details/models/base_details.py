# Copyright 2017 Stanislav Krotov <https://www.it-projects.info/team/ufaks>
# Copyright 2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

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

    details_model_record = fields.Reference(selection="_model_selection", string='Record')
    details_model = fields.Char(compute="_compute_details", string='Detail Model', store=True)
    details_res_id = fields.Integer(compute="_compute_details", string='Details', store=True)
    details_model_exists = fields.Boolean(compute="_compute_details", string='Details Model Exists', store=True)

    @api.multi
    @api.depends('details_model_record')
    @api.onchange('details_model_record')
    def _compute_details(self):
        for rec in self:
            rec.details_model = rec.details_model_record and rec.details_model_record._name
            rec.details_res_id = rec.details_model_record and rec.details_model_record.id
            rec.details_model_exists = (rec.details_model and rec.details_model in rec.env) and True


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
