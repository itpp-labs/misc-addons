# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

import base64
import logging

from odoo import api, models
from odoo.tools import human_size
from odoo.tools.safe_eval import safe_eval

from .res_config_settings import NotAllCredentialsGiven

_logger = logging.getLogger(__name__)

PREFIX = "s3://"


class IrAttachment(models.Model):

    _inherit = "ir.attachment"

    @api.multi
    def _filter_protected_attachments(self):
        return self.filtered(
            lambda r: r.res_model not in ["ir.ui.view", "ir.ui.menu"]
            and not r.name.startswith("/web/content/")
            and not r.name.startswith("/web/static/")
        )

    def _inverse_datas(self):
        our_records = self._filter_protected_attachments()

        if our_records:
            try:
                bucket = self.env["res.config.settings"].get_s3_bucket()
            except NotAllCredentialsGiven:
                _logger.warning("Keeping attachments as usual")
                return super(IrAttachment, self)._inverse_datas()
            except Exception:
                _logger.exception(
                    "Something bad happened with S3. Keeping attachments as usual"
                )
                return super(IrAttachment, self)._inverse_datas()

        for attach in our_records:
            bin_data = base64.b64decode(attach.datas)
            checksum = self._compute_checksum(bin_data)
            fname, url = self._file_write_s3(
                bucket, bin_data, checksum, attach.mimetype
            )
            vals = {
                "file_size": len(bin_data),
                "checksum": checksum,
                "index_content": self._index(
                    bin_data, attach.datas_fname, attach.mimetype
                ),
                "store_fname": fname,
                "db_datas": False,
                "type": "binary",
                "url": url,
                "datas_fname": attach.datas_fname,
            }
            super(IrAttachment, attach.sudo()).write(vals)

        return super(IrAttachment, self - our_records)._inverse_datas()

    def _file_read(self, fname, bin_size=False):
        if not fname.startswith(PREFIX):
            return super(IrAttachment, self)._file_read(fname, bin_size)

        bucket = self.env["res.config.settings"].get_s3_bucket()

        file_id = fname[len(PREFIX) :]
        _logger.debug("reading file with id {}".format(file_id))

        obj = bucket.Object(file_id)
        data = obj.get()

        if bin_size:
            return human_size(data["ContentLength"])
        else:
            return base64.b64encode(b"".join(data["Body"]))

    def _file_write_s3(self, bucket, bin_data, checksum, mimetype):
        file_id = "odoo/{}".format(checksum)

        obj = bucket.put_object(
            Key=file_id, Body=bin_data, ACL="public-read", ContentType=mimetype,
        )

        _logger.debug("uploaded file with id {}".format(file_id))

        location_constraint = obj.meta.client.get_bucket_location(
            Bucket=bucket.name
        ).get("LocationConstraint")
        domain_part = "s3-" + location_constraint if location_constraint else "s3"
        obj_url = "https://{}.amazonaws.com/{}/{}".format(
            domain_part, bucket.name, file_id
        )
        return PREFIX + file_id, obj_url

    def _file_delete(self, fname):
        if not fname.startswith(PREFIX):
            return super(IrAttachment, self)._file_delete(fname)

        bucket = self.env["res.config.settings"].get_s3_bucket()

        file_id = fname[len(PREFIX) :]
        _logger.debug("deleting file with id {}".format(file_id))

        obj = bucket.Object(file_id)
        obj.delete()

    def force_storage_s3(self):
        bucket = self.env["res.config.settings"].get_s3_bucket()

        s3_condition = self.env["ir.config_parameter"].sudo().get_param("s3.condition")
        condition = s3_condition and safe_eval(s3_condition, mode="eval") or []

        attachment_ids = self._search(
            [
                ("store_fname", "not ilike", PREFIX),
                ("store_fname", "!=", False),
                ("res_model", "not in", ["ir.ui.view", "ir.ui.menu"]),
            ]
            + condition
        )

        _logger.info("%s attachments to store to s3" % len(attachment_ids))
        for attach in map(self.browse, attachment_ids):
            is_protected = not bool(attach._filter_protected_attachments())

            if is_protected:
                _logger.info("ignoring protected attachment %s", repr(attach))
                continue
            else:
                _logger.info("storing %s", repr(attach))

            old_store_fname = attach.store_fname
            data = self._file_read(old_store_fname, bin_size=False)
            bin_data = base64.b64decode(data) if data else b""
            checksum = (
                self._compute_checksum(bin_data)
                if not attach.checksum
                else attach.checksum
            )

            new_store_fname, url = self._file_write_s3(
                bucket, bin_data, checksum, attach.mimetype
            )
            attach.write({"store_fname": new_store_fname, "url": url})
            self._file_delete(old_store_fname)
