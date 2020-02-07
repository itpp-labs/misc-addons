# Copyright 2016-2018 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2016-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Alexandr Kolushov <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em230418>
import base64
import hashlib
import logging
import os

from odoo import _, api, exceptions, fields, models, tools
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    import boto3
    import botocore
except Exception:
    _logger.debug(
        "boto3 package is required which is not \
    found on your installation"
    )


class IrAttachmentResized(models.Model):
    _name = "ir.attachment.resized"
    _description = "Url to resized image"

    attachment_id = fields.Many2one("ir.attachment")
    width = fields.Integer()
    height = fields.Integer()
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

    def _get_s3_settings(self, param_name, os_var_name):
        config_obj = self.env["ir.config_parameter"]
        res = config_obj.sudo().get_param(param_name)
        if not res:
            res = os.environ.get(os_var_name)
        return res

    @api.model
    def _get_s3_object_url(self, s3, s3_bucket_name, key_name):
        bucket_location = s3.meta.client.get_bucket_location(Bucket=s3_bucket_name)
        location_constraint = bucket_location.get("LocationConstraint")
        domain_part = "s3" + "-" + location_constraint if location_constraint else "s3"
        object_url = "https://{}.amazonaws.com/{}/{}".format(
            domain_part, s3_bucket_name, key_name
        )
        return object_url

    @api.model
    def _get_s3_resource(self):
        access_key_id = self._get_s3_settings("s3.access_key_id", "S3_ACCESS_KEY_ID")
        secret_key = self._get_s3_settings("s3.secret_key", "S3_SECRET_KEY")
        bucket_name = self._get_s3_settings("s3.bucket", "S3_BUCKET")

        if not access_key_id or not secret_key or not bucket_name:
            _logger.info(
                _(
                    "Amazon S3 credentials are not defined properly. Attachments won't be saved on S3."
                )
            )
            return False

        s3 = boto3.resource(
            "s3", aws_access_key_id=access_key_id, aws_secret_access_key=secret_key
        )
        bucket = s3.Bucket(bucket_name)
        if not bucket:
            s3.create_bucket(Bucket=bucket_name)
        return s3

    def _inverse_datas(self):
        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ir_attachment_url.storage")
            != "s3"
        ):
            return super(IrAttachment, self)._inverse_datas()

        condition = self._get_s3_settings("s3.condition", "S3_CONDITION")
        if condition and not self.env.context.get("force_s3"):
            condition = safe_eval(condition, mode="eval")
            s3_records = self.sudo().search([("id", "in", self.ids)] + condition)
        else:
            # if there is no condition or force_s3 in context
            # then store all attachments on s3
            s3_records = self

        if s3_records:
            s3 = self._get_s3_resource()
            if not s3:
                _logger.info("something wrong on aws side, keep attachments as usual")
                s3_records = self.env[self._name]
            else:
                s3_records = s3_records._filter_protected_attachments()
                s3_records = s3_records.filtered(lambda r: r.type != "url")

        resized_to_remove = self.env["ir.attachment.resized"].sudo()
        for attach in (
            self & s3_records
        ):  # datas field has got empty somehow in the result of ``s3_records = self.sudo().search([('id', 'in', self.ids)] + condition)`` search for non-superusers but it is in original recordset. Here we use original (with datas) in case it intersects with the search result
            resized_to_remove |= attach.sudo().resized_ids
            value = attach.datas
            bin_data = base64.b64decode(value) if value else b""
            fname = hashlib.sha1(bin_data).hexdigest()
            bucket_name = self._get_s3_settings("s3.bucket", "S3_BUCKET")
            try:
                s3.Bucket(bucket_name).put_object(
                    Key=fname,
                    Body=bin_data,
                    ACL="public-read",
                    ContentType=attach.mimetype,
                )
            except botocore.exceptions.ClientError as e:
                raise exceptions.UserError(str(e))

            vals = {
                "file_size": len(bin_data),
                "checksum": self._compute_checksum(bin_data),
                "index_content": self._index(
                    bin_data, attach.datas_fname, attach.mimetype
                ),
                "store_fname": fname,
                "db_datas": False,
                "type": "url",
                "url": self._get_s3_object_url(s3, bucket_name, fname),
            }
            super(IrAttachment, attach.sudo()).write(vals)

        resized_to_remove.mapped("resized_attachment_id").unlink()
        resized_to_remove.unlink()
        super(IrAttachment, self - s3_records)._inverse_datas()

    @api.model
    def _get_context_variants_for_resized_att_creating(self):
        return {"s3": {"force_s3": True}}

    def _get_context_for_resized_att_creating(self):
        url_storage = self.env["ir.config_parameter"].get_param(
            "ir_attachment_url.storage", default="url"
        )
        return (
            self._get_context_variants_for_resized_att_creating().get(url_storage) or {}
        )

    @api.model
    def _get_or_create_resized_in_cache(self, width, height, field=None):
        return self._get_resized_from_cache(
            width, height
        ) or self._set_resized_to_cache(width, height, field)

    @api.model
    def _get_resized_from_cache(self, width, height):
        return (
            self.env["ir.attachment.resized"]
            .sudo()
            .search(
                [
                    ("attachment_id", "=", self.id),
                    ("width", "=", width),
                    ("height", "=", height),
                ]
            )
        )

    @api.model
    def _set_resized_to_cache(self, width, height, field=None):
        content = self.datas
        content = tools.image_resize_image(
            base64_source=content,
            size=(width or None, height or None),
            encoding="base64",
            filetype="PNG",
        )

        new_resized_attachment_data = {
            "name": "{}x{} {}".format(width, height, self.name),
            "datas": content,
        }
        if field:
            new_resized_attachment_data.update(
                {"res_model": self.res_model, "res_field": field, "res_id": self.res_id}
            )
        context = self._get_context_for_resized_att_creating()
        resized_attachment = (
            self.env["ir.attachment"]
            .with_context(context)
            .sudo()
            .create(new_resized_attachment_data)
        )
        return (
            self.env["ir.attachment.resized"]
            .sudo()
            .create(
                {
                    "attachment_id": self.id,
                    "width": width,
                    "height": height,
                    "resized_attachment_id": resized_attachment.id,
                }
            )
        )
