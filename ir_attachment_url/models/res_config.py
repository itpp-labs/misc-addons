# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2019 Alexandr Kolushov <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019-2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class IrAttachmentSettings(models.TransientModel):
    _name = "ir.attachment.config.settings"
    _inherit = "res.config.settings"

    ir_attachment_url_storage = fields.Selection(
        selection=[("url", "Save as original link")],
        default="url",
        string="Attachment storage",
        required=True,
    )

    def set_values(self):
        super(IrAttachmentSettings, self).set_values()
        self.env["ir.config_parameter"].set_param(
            "ir_attachment_url.storage", self.ir_attachment_url_storage or "url",
        )

    @api.model
    def get_values(self):
        res = super(IrAttachmentSettings, self).get_values()
        res.update(
            ir_attachment_url_storage=self.env["ir.config_parameter"].get_param(
                "ir_attachment_url.storage", default="url"
            )
        )
        return res
