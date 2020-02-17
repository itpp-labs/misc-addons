# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2019 Alexandr Kolushov <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class IrAttachmentSettings(models.TransientModel):
    _name = "ir.attachment.config.settings"
    _inherit = "res.config.settings"

    ir_attachment_url_storage = fields.Selection(
        selection=[("url", "Save as original link")],
        default="url",
        string="Attachment storage",
        required=True,
    )

    def get_default_all(self, fields):
        ir_attachment_url_storage = self.env["ir.config_parameter"].get_param(
            "ir_attachment_url.storage", default="url"
        )
        return dict(ir_attachment_url_storage=ir_attachment_url_storage)
