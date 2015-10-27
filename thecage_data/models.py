# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SaleOrderWithSms(models.Model):
    _inherit = 'sale.order'

    @api.one
    def write(self, vals):
        result = super(SaleOrderWithSms, self).write(vals)
        if vals.get('state') == 'sent':
            msg = 'Sale Order #' + self.name + ' is confirmed'
            phone = self.partner_id.mobile
            self.env['sms_sg.sendandlog'].send_sms(phone, msg)
        return result
