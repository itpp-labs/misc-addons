# Copyright 2016-2018 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2016-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IrAttachmentResized(models.Model):
    _name = "ir.attachment.resized"
    _description = "Resized image"

    attachment_id = fields.Many2one("ir.attachment")
    width = fields.Integer()
    height = fields.Integer()
    crop = fields.Boolean()
    resized_attachment_id = fields.Many2one("ir.attachment", ondelete="cascade")

    @api.multi
    def unlink(self):
        # we also unlink resized_attachment_id
        resized_att_id = self.resized_attachment_id
        super(IrAttachmentResized, self).unlink()
        return resized_att_id.unlink()


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    resized_ids = fields.One2many("ir.attachment.resized", "attachment_id")

    @api.multi
    def unlink(self):
        resized_ids = self.mapped("resized_ids")
        super(IrAttachment, self).unlink()
        # we also need to delete, resized attachments if given
        # to escape RecursionError, we need to check it first
        return resized_ids.unlink() if resized_ids else True

    @api.model
    def get_resized_from_cache(self, width, height, crop):
        return (
            self.env["ir.attachment.resized"]
            .sudo()
            .search(
                [
                    ("attachment_id", "=", self.id),
                    ("width", "=", width),
                    ("height", "=", height),
                    ("crop", "=", crop),
                ],
                limit=1,
            )
        )

    @api.model
    def store_resized_to_cache(self, content, width, height, crop):
        new_resized_attachment_data = {
            "name": "{}x{} {} {}".format(
                width,
                height,
                self.name or "noname",
                "cropped" if crop else "not cropped",
            ),
            "datas": content,
            # adding res_model and res_id is required not to have AccessError
            "res_model": self.res_model,
            "res_id": self.res_id,
        }
        resized_attachment = (
            self.env["ir.attachment"].sudo().create(new_resized_attachment_data)
        )
        return (
            self.env["ir.attachment.resized"]
            .sudo()
            .create(
                {
                    "attachment_id": self.id,
                    "width": width,
                    "height": height,
                    "crop": crop,
                    "resized_attachment_id": resized_attachment.id,
                }
            )
        )
