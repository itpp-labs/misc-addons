# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.exceptions import ValidationError
from openerp.tools.translate import _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'


    remind_on_slots = fields.Integer(help='configure when to remind a customer about remaining slots', string='Remind on (slots)', default=2)
    contract_slots = fields.Integer(string='Contract slots left', compute='_compute_contract_slots', readonly=True, help='remaining paid slots in contract', store=True)
    type = fields.Selection(default='contract')
    order_line_ids = fields.One2many('sale.order.line', 'contract_id')
    invoice_line_ids = fields.One2many('account.invoice.line', 'account_analytic_id')

    @api.one
    @api.depends('invoice_line_ids.invoice_id.state', 'order_line_ids.booking_state')
    def _compute_contract_slots(self):
        contract_slots = 0


        invoice_line_obj = self.env['account.invoice.line']
        contract_slots += invoice_line_obj.search_count([('account_analytic_id', '=', self.id),
                                                                         ('invoice_id.state', '=', 'paid'),
                                                                         ('invoice_id.type', '=', 'out_invoice')])
        contract_slots -= invoice_line_obj.search_count([('account_analytic_id', '=', self.id),
                                                                         ('invoice_id.state', '=', 'paid'),
                                                                         ('invoice_id.type', '=', 'out_refund')])
        contract_slots -= len(self.order_line_ids.filtered(lambda r: r.booking_state in ['consumed', 'no_show']))
        self.contract_slots = contract_slots

    @api.model
    def _cron_expiring_reminder(self):
        # TODO: send email and sms if contract_slots are less than remind_on_slots. send sms only. send email only
        pass


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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    active = fields.Boolean(default=True, compute='_compute_line_active', store='True')
    booking_reminder = fields.Boolean(default=False, select=True)
    booking_state = fields.Selection([('in_progress', 'In Progress'),
                                      ('consumed', 'Consumed'),
                                      ('no_show', 'No Show'),
                                      ('rain_check', 'Rain Check'),
                                      ('emergency', 'Emergency'),
                                      ('cancelled', 'Cancelled')],
                                     default='in_progress', required='True')

    @api.multi
    @api.depends('booking_state')
    def _compute_line_active(self):
        for line in self:
            line.active = line.booking_state != 'cancelled'

    @api.model
    def _cron_booking_reminder(self):
        lines = self.search(['&', '&', '&', ('booking_reminder', '=', False),
                             ('booking_start', '!=', False),
                             ('booking_start', '<=', (datetime.now() + timedelta(hours=48)).strftime(DTF)),
                             '|',
                             ('order_id.state', '=', 'done'),
                             ('price_unit', '=', '0'),
                             ])
        lines.write({'booking_reminder': True})
        for line in lines:
            msg = 'Sale Order #' + line.order_id.name + ' is confirmed'
            phone = line.order_id.partner_id.mobile
            self.env['sms_sg.sendandlog'].send_sms(phone, msg)

    @api.multi
    def write(self, values):
        for line in self:
            if 'booking_start' in values:
                if datetime.strptime(values['booking_start'], DTF) < datetime.strptime(line.booking_start, DTF):
                    raise ValidationError(_('You can move booking forward only.'))
        return super(SaleOrderLine, self).write(values)


class ResPartnerReminderConfig(models.Model):
    _inherit = 'res.partner'

    reminder_sms = fields.Boolean(default=True, string='Booking sms reminder enabled')
    reminder_email = fields.Boolean(default=True, string='Booking email reminder enabled')


class GenerateBookingWizard(models.TransientModel):
    _name = 'thecage_data.generate_booking_wizard'

    quantity = fields.Integer(string='Number of bookings to generate', default=51)
    product_id = fields.Many2one('product.product', string='Product')
    venue_id = fields.Many2one('pitch_booking.venue', string='Venue', related='product_id.venue_id')
    pitch_id = fields.Many2one('pitch_booking.pitch', string='Pitch')
    booking_start = fields.Datetime(string='Booking start')
    booking_end = fields.Datetime(string='Booking end')
    product_uom_qty = fields.Integer()

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
        if len(active_order.order_line) > 0:
            result.update({
                'product_id': active_order.order_line[0].product_id.id,
                'pitch_id': active_order.order_line[0].pitch_id.id,
                'booking_start': active_order.order_line[0].booking_start,
                'booking_end': active_order.order_line[0].booking_end,
            })
        return result

    @api.onchange('booking_start', 'booking_end')
    def _on_change_booking_time(self):
        if self.booking_start and self.booking_end:
            start = datetime.strptime(self.booking_start, DTF)
            end = datetime.strptime(self.booking_end, DTF)
            self.product_uom_qty = (end - start).seconds/3600

    @api.one
    @api.depends('booking_start')
    def _compute_day_of_week(self):
        dt = self.booking_start and datetime.strptime(self.booking_start, DTF)
        self.day_of_week = dt and date(dt.year, dt.month, dt.day).weekday()

    @api.multi
    def generate_booking_lines(self):
        active_id = self.env.context and self.env.context.get('active_id', False)
        active_order = self.env['sale.order'].browse(active_id)
        booking_start = datetime.strptime(self.booking_start, DTF)
        booking_end = datetime.strptime(self.booking_end, DTF)

        for line in range(0, self[0].quantity):
            booking_start = booking_start + timedelta(days=7)
            booking_end = booking_end + timedelta(days=7)

            self.env['sale.order.line'].create({'order_id': active_order.id,
                                                'product_id': self[0].product_id.id,
                                                'venue_id': self[0].venue_id.id,
                                                'pitch_id': self[0].pitch_id.id,
                                                'product_uom_qty': self[0].product_uom_qty,
                                                'booking_start': booking_start,
                                                'booking_end': booking_end,
                                                'automatic': True,
                                                'state': 'draft'})
