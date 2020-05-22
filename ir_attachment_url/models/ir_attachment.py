import base64

import requests

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.depends("store_fname", "db_datas")
    def _compute_datas(self):
        attachment_return_url = self._context.get("attachment_return_url")
        bin_size = self._context.get("bin_size")
        url_records = self.filtered(lambda r: r.type == "url" and r.url)
        for attach in url_records:
            if not bin_size:
                if attachment_return_url:
                    attach.datas = attach.url
                    continue
                r = requests.get(attach.url, timeout=5)
                attach.datas = base64.b64encode(r.content)
            else:
                attach.datas = "1.00 Kb"

        super(IrAttachment, self - url_records)._compute_datas()

    @api.multi
    def _filter_protected_attachments(self):
        return self.filtered(
            lambda r: r.res_model not in ["ir.ui.view", "ir.ui.menu"]
            or not r.name.startswith("/web/content/")
        )
