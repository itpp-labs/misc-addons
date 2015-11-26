# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AccountAnalyticAccountUsedSlots(models.Model):
    _inherit = 'account.analytic.account'

    used_slots = fields.Integer(default=0, help='number of used slots', readonly=True)
    remind_on_slots = fields.Integer(help='configure when to remind a customer about remaining slots', string='Remind on (slots)', default=2)

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
        # send sms immediately after user pushed 'Send by Email' button on the Sale Order
        if vals.get('state') == 'sent' and self.partner_id.reminder_sms:
                msg = 'Sale Order #' + self.name + ' is confirmed'
                phone = self.partner_id.mobile
                self.env['sms_sg.sendandlog'].send_sms(phone, msg)
        return result

    @api.multi
    def remove_generated_lines(self):
        records = self.env['sale.order.line'].search([('order_id', '=', self[0].id), ('automatic', '=', True)])
        records.button_cancel()
        records.unlink()


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


class ResPartnerReminderConfig(models.Model):
    _inherit = 'res.partner'

    reminder_sms = fields.Boolean(default=True, string='Booking sms reminder enabled')
    reminder_email = fields.Boolean(default=True, string='Booking email reminder enabled')


class GenerateBookingWizard(models.TransientModel):
    _name = 'thecage_data.generate_booking_wizard'

    quantity = fields.Integer(string='Number of bookings to generate', default=52)
    product_id = fields.Many2one('product.product', string='Product')
    venue_id = fields.Many2one('pitch_booking.venue', string='Venue', related='product_id.venue_id')
    pitch_id = fields.Many2one('pitch_booking.pitch', string='Pitch')
    booking_start = fields.Datetime(string='Booking start')
    booking_end = fields.Datetime(string='Booking end')

    day_of_week = fields.Selection([(0, 'Monday'),
                                    (1, 'Tuesday'),
                                    (2, 'Wednesday'),
                                    (3, 'Thursday'),
                                    (4, 'Friday'),
                                    (5, 'Saturday'),
                                    (6, 'Sunday')],
                                   compute='_compute_day_of_week', readonly=True)

    def default_get(self, cr, uid, fields, context=None):
        result = super(GenerateBookingWizard, self).default_get(cr, uid, fields, context=context)
        active_id = context and context.get('active_id', False)
        active_order = self.pool['sale.order'].browse(cr, uid, active_id, context=context)
        result.update({
            'product_id': active_order.order_line[0].product_id.id,
            'pitch_id': active_order.order_line[0].pitch_id.id,
            'booking_start': active_order.order_line[0].booking_start,
            'booking_end': active_order.order_line[0].booking_end
        })
        return result

    @api.one
    @api.depends('booking_start')
    def _compute_day_of_week(self):
        dt = datetime.strptime(self.booking_start, DEFAULT_SERVER_DATETIME_FORMAT)
        self.day_of_week = date(dt.year, dt.month, dt.day).weekday()

    @api.multi
    def generate_booking_lines(self):
        active_id = self.env.context and self.env.context.get('active_id', False)
        active_order = self.env['sale.order'].browse(active_id)
        booking_start = datetime.strptime(self.booking_start, DEFAULT_SERVER_DATETIME_FORMAT)
        booking_end = datetime.strptime(self.booking_end, DEFAULT_SERVER_DATETIME_FORMAT)

        for line in range(0, self[0].quantity):
            booking_start = booking_start + timedelta(days=7)
            booking_end = booking_end + timedelta(days=7)

            self.env['sale.order.line'].create({'order_id': active_order.id,
                                                'product_id': self[0].product_id.id,
                                                'venue_id': self[0].venue_id.id,
                                                'pitch_id': self[0].pitch_id.id,
                                                'booking_start': booking_start,
                                                'booking_end': booking_end,
                                                'automatic': True,
                                                'state': 'draft'})
