# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


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


class SaleOrderLineReminder(models.Model):
    _inherit = 'sale.order.line'

    reminded = fields.Boolean(default=False, select=True)

    @api.model
    def _cron_reminder(self):
        lines = self.search([('reminded', '=', False),
                             ('booking_start', '!=', False),
                             ('order_id.state', '=', 'done'),
                             ('booking_start', '<=', (datetime.now() + timedelta(hours=48)).strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
        lines.write({'reminded': True})
        for line in lines:
            msg = 'Sale Order #' + line.order_id.name + ' is confirmed'
            phone = line.order_id.partner_id.mobile
            self.env['sms_sg.sendandlog'].send_sms(phone, msg)
