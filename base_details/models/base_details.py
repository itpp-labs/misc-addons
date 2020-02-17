# Copyright 2017 Stanislav Krotov <https://www.it-projects.info/team/ufaks>
# Copyright 2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class BaseDetails(models.AbstractModel):
    """Model to be inherited by Model where details field has to be added"""

    _name = "base_details"

    def _model_selection(self):
        return []

    @api.depends("details_model")
    def _details_model_record_selection(self):
        selection = []
        for x in self._model_selection():
            if x[0] in [x.model for x in self.env["ir.model"].search([])]:
                selection.append(x)
        return selection

    @property
    def details(self):
        if (
            self.details_model
            and self.details_model in self.env
            and self.details_res_id
        ):
            details_record = self.env[self.details_model].browse(self.details_res_id)
        else:
            details_record = None
        return details_record

    details_model = fields.Selection(selection="_model_selection", string="Model")
    details_model_record = fields.Reference(
        selection="_details_model_record_selection", string="Record"
    )
    details_model_exists = fields.Boolean(
        compute="_compute_existence", string="Details Model Exists", store=True
    )
    details_res_id = fields.Integer(
        compute="_compute_res_id", string="Record", store=True
    )

    @api.onchange("details_model")
    def onchange_details_model(self):
        if self.details_model and self.details_model in [
            x.model for x in self.env["ir.model"].search([])
        ]:
            self.details_model_exists = True
            # set to random record so we don't need to select model again
            self.details_model_record = self.env[self.details_model].search([], limit=1)
        else:
            self.details_model_exists = False
            self.details_model_record = False

    @api.multi
    @api.depends("details_model")
    def _compute_existence(self):
        for rec in self:
            if rec.details_model and rec.details_model in [
                x.model for x in rec.env["ir.model"].search([])
            ]:
                rec.details_model_exists = True
            else:
                rec.details_model_exists = False

    @api.multi
    @api.onchange("details_model_exists", "details_model_record")
    def _compute_res_id(self):
        for rec in self:
            if rec.details_model_exists:
                rec.details_res_id = (
                    rec.details_model_record and rec.details_model_record.id
                )
                if rec.details_model_record:
                    rec.details_model = rec.details_model_record._name
            else:
                rec.details_res_id = False


class BaseDetailsRecord(models.AbstractModel):
    """Model to be inherited by Model with details"""

    _name = "base_details_record"
    _base_details_model = "UPDATE_THIS"

    @api.multi
    def _base_details_reversed(self):
        reversed_records = self.env[self._base_details_model].search_read(
            [("details_model", "=", self._name), ("details_res_id", "in", self.ids)],
            fields=["id", "details_res_id"],
        )
        return ((r["details_res_id"], r["id"]) for r in reversed_records)
