# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SaleOrderWithSms(models.Model):
    _inherit = 'sale.order'

    @api.one
    def write(self, vals):
        result = super(SaleOrderWithSms, self).write(vals)
        if vals.get('state') == 'sent':
            self.env['sms_sg.sndandlog'].send_sms('9177825074', 'Hello, World!')
        return result
