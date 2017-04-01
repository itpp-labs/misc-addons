# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Preview(models.AbstractModel):
    _name = "web.preview"

    media_type = fields.Char('Type', compute='_compute_type')
    media_filename = fields.Char("File Name")

    @api.multi
    def _compute_type(self):
        for r in self:
            attachment = self.env["ir.attachment"]
            r.media_type = attachment.search([('res_model', '=', self._name), ('res_field', '=', r._preview_media_file),
                                                 ('res_id', '=', r.id)]).mimetype
