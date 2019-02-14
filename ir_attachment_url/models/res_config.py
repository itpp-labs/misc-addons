# -*- coding: utf-8 -*-

from odoo import models, fields


class IrAttachmentSettings(models.TransientModel):
    _name = 'ir.attachment.config.settings'
    _inherit = 'res.config.settings'

    ir_attachment_save_option = fields.Selection(
        selection=[('url', 'Save as original link')],
        default='url',
        string='Way to save attachments',
        required=True,
    )

    def set_ir_attachment_save_option(self):
        self.env['ir.config_parameter'].set_param(
            "ir_attachment.save_option",
            self.ir_attachment_save_option or 'url',
            groups=['base.group_system'],
        )

    def get_default_all(self, fields):
        ir_attachment_save_option = self.env["ir.config_parameter"].get_param("ir_attachment.save_option", default='url')
        return dict(
            ir_attachment_save_option=ir_attachment_save_option,
        )
