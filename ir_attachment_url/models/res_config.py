# -*- coding: utf-8 -*-

from odoo import models, fields


class IrAttachmentSettings(models.TransientModel):
    _name = 'ir.attachment.config.settings'
    _inherit = 'res.config.settings'

    ir_attachment_url_storage = fields.Selection(
        selection=[('url', 'Save as original link')],
        default='url',
        string='Attachment storage',
        required=True,
    )

    def set_ir_attachment_url_storage(self):
        self.env['ir.config_parameter'].set_param(
            "ir_attachment_url.storage",
            self.ir_attachment_url_storage or 'url',
            groups=['base.group_system'],
        )

    def get_default_all(self, fields):
        ir_attachment_url_storage = self.env["ir.config_parameter"].get_param("ir_attachment_url.storage", default='url')
        return dict(
            ir_attachment_url_storage=ir_attachment_url_storage,
        )
