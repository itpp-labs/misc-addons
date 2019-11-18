import requests
import base64
from odoo import api, models
from . import image

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _inverse_datas(self):
        if self.env['ir.config_parameter'].sudo().get_param('ir_attachment_url.storage') != 'url':
            return super(IrAttachment, self)._inverse_datas()

        url_records = self.filtered(lambda r: image.is_url(r.datas))
        for attach in url_records:
            value = attach.datas
            bin_data = bytearray(value, 'utf-8')
            vals = {
                'checksum': self._compute_checksum(bin_data),
                'index_content': self._index(bin_data, attach.datas_fname, attach.mimetype),
                'store_fname': False,
                'db_datas': False,
                'url': value,
                'type': 'url',
            }
            super(IrAttachment, attach.sudo()).write(vals)

        super(IrAttachment, self - url_records)._inverse_datas()

    @api.depends('store_fname', 'db_datas')
    def _compute_datas(self):
        bin_size = self._context.get('bin_size')
        url_records = self.filtered(lambda r: r.type == 'url' and r.url)
        for attach in url_records:
            if not bin_size:
                r = requests.get(attach.url, timeout=5)
                attach.datas = base64.b64encode(r.content)
            else:
                attach.datas = "1.00 Kb"

        super(IrAttachment, self - url_records)._compute_datas()

    def _filter_protected_attachments(self):
        return self.filtered(lambda r: r.res_model not in ['ir.ui.view', 'ir.ui.menu'] or not r.name.startswith('/web/content/'))
