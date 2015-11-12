# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AccountAnalyticAccountUsedSlots(models.Model):
    _inherit = 'account.analytic.account'

    used_slots = fields.Integer(default=0, help='number of used slots', readonly=True)

    @api.model
    def _cron_compute_used_slots(self):
        for record in self.search([]):
            lines = self.env['sale.order.line'].search([
                ('order_id.project_id', '=', record.id),
                ('booking_end', '!=', False),
                ('booking_end', '<=', datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ('order_id.state', 'in', ['manual', 'done']),
                ('price_unit', '=', '0'),
            ])
            uslots = 0
            for line in lines:
                uslots += line.product_uom_qty

            record.used_slots = uslots


class SaleOrderTheCage(models.Model):
    _inherit = 'sale.order'

    expiring_reminder = fields.Boolean(default=False)

    @api.one
    def write(self, vals):
        result = super(SaleOrderTheCage, self).write(vals)
        if vals.get('state') == 'sent':
            msg = 'Sale Order #' + self.name + ' is confirmed'
            phone = self.partner_id.mobile
            self.env['sms_sg.sendandlog'].send_sms(phone, msg)
        return result


class SaleOrderLineReminder(models.Model):
    _inherit = 'sale.order.line'

    booking_reminder = fields.Boolean(default=False, select=True)

    @api.model
    def _cron_booking_reminder(self):
        lines = self.search(['&', '&', '&', ('booking_reminder', '=', False),
                             ('booking_start', '!=', False),
                             ('booking_start', '<=', (datetime.now() + timedelta(hours=48)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                             '|',
                             ('order_id.state', '=', 'done'),
                             ('price_unit', '=', '0'),
                             ])
        lines.write({'booking_reminder': True})
        for line in lines:
            msg = 'Sale Order #' + line.order_id.name + ' is confirmed'
            phone = line.order_id.partner_id.mobile
            self.env['sms_sg.sendandlog'].send_sms(phone, msg)
