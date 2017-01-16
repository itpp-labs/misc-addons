# -*- coding: utf-8 -*-
import pytz
from pytz import timezone
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.exceptions import ValidationError


def format_tz(datetime_str, tz, dtf):
    datetime_obj = datetime.strptime(datetime_str, dtf)
    user_timezone = timezone(tz)
    datetime_obj = pytz.utc.localize(datetime_obj)
    datetime_obj = datetime_obj.astimezone(user_timezone)
    return datetime_obj.strftime(dtf)


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

        for l in self.invoice_line_ids:
            contract_slots += not l.pitch_id.resource_id.has_slot_calendar and l.invoice_id.state == 'paid' and l.invoice_id.type == 'out_invoice' and l.quantity or \
                not l.pitch_id.resource_id.has_slot_calendar and l.invoice_id.state == 'paid' and l.invoice_id.type == 'out_refund' and -l.quantity or \
                l.pitch_id.resource_id.has_slot_calendar and l.invoice_id.state == 'paid' and l.invoice_id.type == 'out_invoice' and l.quantity / 2 or \
                l.pitch_id.resource_id.has_slot_calendar and l.invoice_id.state == 'paid' and l.invoice_id.type == 'out_refund' and -l.quantity / 2

        for l in self.order_line_ids:
            contract_slots += not l.pitch_id.resource_id.has_slot_calendar and l.booking_state in ['consumed', 'no_show'] and -l.product_uom_qty or \
                l.pitch_id.resource_id.has_slot_calendar and l.booking_state in ['consumed', 'no_show'] and -l.product_uom_qty / 2

        self.contract_slots = contract_slots

    @api.model
    def _cron_expiring_reminder(self):
        # TODO: send email and sms if contract_slots are less than remind_on_slots. send sms only. send email only
        pass


class SaleOrderTheCage(models.Model):
    _inherit = 'sale.order'

    expiring_reminder = fields.Boolean(default=False)

    @api.multi
    def write(self, vals):
        result = super(SaleOrderTheCage, self).write(vals)
        for r in self:
            # send sms immediately after user pushed 'Send by Email' button on the Sale Order
            if vals.get('state') == 'sent' and r.partner_id.confirmation_sms:
                phone = r.partner_id.mobile
                for line in r.order_line.filtered(lambda r: r.pitch_id):  # filter not bookings
                    msg = 'Successfully booked a pitch at The Cage %s!\n' % line.venue_id.name
                    msg += 'Pitch %s\n' % line.pitch_id.name
                    msg += 'From: %s To %s\n' % (format_tz(line.booking_start, self.env.user.tz, DTF),
                                                 format_tz(line.booking_end, self.env.user.tz, DTF))
                    msg += 'ID %s\n' % r.name
                    self.env['sms_sg.sendandlog'].send_sms(phone, msg)
        return result

    @api.multi
    def remove_generated_lines(self):
        records = self.env['sale.order.line'].search([('order_id', '=', self[0].id), ('automatic', '=', True)])
        records.button_cancel()
        records.unlink()


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['mail.thread', 'sale.order.line']

    active = fields.Boolean(default=True, compute='_compute_line_active', store='True')
    booking_reminder = fields.Boolean(default=False, select=True)
    booking_state = fields.Selection('_get_booking_states', default='in_progress', required='True', track_visibility='onchange')

    booking_end = fields.Datetime(track_visibility='onchange')
    booking_start = fields.Datetime(track_visibility='onchange')
    venue_id = fields.Many2one(track_visibility='onchange')
    pitch_id = fields.Many2one(track_visibility='onchange')
    product_id = fields.Many2one(track_visibility='onchange')

    @api.multi
    def write(self, vals):
        result = super(SaleOrderLine, self).write(vals)
        for r in self:
            if vals.get('booking_start') or vals.get('booking_end'):
                r.send_booking_time()
        return result


    @api.multi
    def send_booking_time(self):
        for r in self:
            r.send_booking_time_one()
        return True

    @api.multi
    def send_booking_time_one(self):
        self.ensure_one()
        if self.booking_start and self.booking_end:
            template = self.env.ref('thecage_data.email_template_booking_time_updated')
            email_ctx = {
                'default_model': 'sale.order.line',
                'default_res_id': self.id,
                'default_use_template': bool(template),
                'default_template_id': template.id,
                'default_composition_mode': 'comment',
            }
            composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
            composer.send_mail()

    @api.model
    def _get_booking_states(self):
        states = [('in_progress', 'In Progress'),
                  ('consumed', 'Consumed'),
                  ('no_show', 'No Show'),
                  ('rain_check', 'Rain Check'),
                  ('emergency', 'Emergency')]
        if self.env.ref('base.group_sale_manager').id in self.env.user.groups_id.ids:
            states.append(('cancelled', 'Cancelled'))

        return states

    @api.multi
    @api.depends('order_id.state', 'booking_state')
    def _compute_line_active(self):
        for line in self:
            line.active = line.booking_state != 'cancelled' and line.order_id.state != 'cancel'

    @api.model
    def _cron_booking_reminder(self):
        lines72 = self.search([('booking_reminder', '=', False),
                               ('booking_start', '!=', False),
                               ('booking_start', '<=', (datetime.now() + timedelta(hours=72)).strftime(DTF))])
        lines48 = self.search([('booking_reminder', '=', False),
                               ('booking_start', '!=', False),
                               ('booking_start', '<=', (datetime.now() + timedelta(hours=48)).strftime(DTF))])
        lines = lines72 - lines48
        lines.write({'booking_reminder': True})
        for line in lines:
            if line.order_id.partner_id.reminder_sms:
                msg = 'Your game at The Cage %s is coming up soon!\n' % line.venue_id.name
                msg += 'Pitch %s\n' % line.pitch_id.name
                msg += 'From: %s To %s\n' % (format_tz(line.booking_start, self.env.user.tz, DTF),
                                             format_tz(line.booking_end, self.env.user.tz, DTF))
                msg += 'ID %s\n' % line.order_id.name
                phone = line.order_id.partner_id.mobile
                self.env['sms_sg.sendandlog'].send_sms(phone, msg)

            if line.order_id.partner_id.reminder_email:
                template = self.env.ref('thecage_data.email_template_booking_reminder')
                email_ctx = {
                    'default_model': 'sale.order.line',
                    'default_res_id': line.id,
                    'default_use_template': bool(template),
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                }
                composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
                composer.send_mail()


class ResPartnerReminderConfig(models.Model):
    _inherit = 'res.partner'

    confirmation_email = fields.Boolean(default=True, string='Booking email confirmation enabled')
    confirmation_sms = fields.Boolean(default=True, string='Booking sms confirmation enabled')
    reminder_sms = fields.Boolean(default=True, string='Booking sms reminder enabled')
    reminder_email = fields.Boolean(default=True, string='Booking email reminder enabled')


class LinesWizard(models.TransientModel):
    _name = 'thecage_data.lines_wizard'

    booking_start = fields.Datetime(string='Booking start')
    booking_end = fields.Datetime(string='Booking end')
    pitch_id = fields.Many2one('pitch_booking.pitch', string='Pitch')
    booking_id = fields.Many2one('thecage_data.generate_booking_wizard')
    overlap = fields.Boolean(default=False)

    @api.multi
    def find_overlaps(self, pitch_id, booking_start, booking_end):
        overlaps = 0
        overlaps = self.env['sale.order.line'].search_count(['&', '|', '&', ('booking_start', '>=', booking_start), ('booking_start', '<', booking_end),
                                                             '&', ('booking_end', '>', booking_start), ('booking_end', '<=', booking_end),
                                                             ('pitch_id', '!=', False),
                                                             ('pitch_id', '=', pitch_id)])
        overlaps += self.env['sale.order.line'].search_count([('booking_start', '=', booking_start),
                                                              ('booking_end', '=', booking_end),
                                                              ('pitch_id', '=', pitch_id)])
        return overlaps

    @api.multi
    @api.onchange('pitch_id', 'booking_start', 'booking_end')
    def _on_change_overlap(self):
        for line in self:
            overlaps = 0
            if line.pitch_id and line.booking_start and line.booking_end:
                overlaps = self.find_overlaps(pitch_id=line.pitch_id.id, booking_start=line.booking_start, booking_end=line.booking_end)
            line.overlap = bool(overlaps)


class GenerateBookingWizard(models.TransientModel):
    _name = 'thecage_data.generate_booking_wizard'

    quantity = fields.Integer(string='Number of bookings to generate', default=51)
    product_id = fields.Many2one('product.product', string='Product')
    venue_id = fields.Many2one('pitch_booking.venue', string='Venue', related='product_id.venue_id')
    pitch_id = fields.Many2one('pitch_booking.pitch', string='Pitch')
    booking_start = fields.Datetime(string='Booking start')
    booking_end = fields.Datetime(string='Booking end')
    product_uom_qty = fields.Integer()
    order_id = fields.Integer()
    line_ids = fields.One2many('thecage_data.lines_wizard', 'booking_id')

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
                'order_id': active_order.id,
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
            self.product_uom_qty = (end - start).seconds / 3600

    @api.one
    @api.depends('booking_start')
    def _compute_day_of_week(self):
        dt = self.booking_start and datetime.strptime(self.booking_start, DTF)
        self.day_of_week = dt and date(dt.year, dt.month, dt.day).weekday()

    @api.multi
    def clear_booking_lines(self):
        self.write({'line_ids': [(5, 0, 0)]})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'thecage_data.generate_booking_wizard',
            'res_id': self[0].id,
            'target': 'new'
        }

    @api.multi
    def generate_booking_lines(self):
        booking_start = datetime.strptime(self.booking_start, DTF)
        booking_end = datetime.strptime(self.booking_end, DTF)

        for line in range(0, self[0].quantity):
            booking_start = booking_start + timedelta(days=7)
            booking_end = booking_end + timedelta(days=7)
            overlap = bool(self.env['thecage_data.lines_wizard'].find_overlaps(
                pitch_id=self[0].pitch_id.id,
                booking_start=booking_start.strftime(DTF),
                booking_end=booking_end.strftime(DTF)))

            self.write({
                'line_ids': [(0, 0, {'booking_start': booking_start,
                                     'booking_end': booking_end,
                                     'pitch_id': self[0].pitch_id.id,
                                     'overlap': overlap})]})

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'thecage_data.generate_booking_wizard',
            'res_id': self[0].id,
            'target': 'new'
        }

    @api.multi
    def add_booking_lines(self):
        for line in self[0].line_ids:
            if line.overlap:
                raise ValidationError('There are bookings with overlapping time')

        for line in self[0].line_ids:
            self.env['sale.order.line'].create({'order_id': self[0].order_id,
                                                'product_id': self[0].product_id.id,
                                                'venue_id': self[0].venue_id.id,
                                                'pitch_id': line.pitch_id.id,
                                                'product_uom_qty': self[0].product_uom_qty,
                                                'booking_start': line.booking_start,
                                                'booking_end': line.booking_end,
                                                'automatic': True,
                                                'state': 'draft'})


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_validate(self):
        for invoice_obj in self.filtered(lambda r: r.type == 'out_refund'):
            for invoice_line_obj in invoice_obj.invoice_line:
                bookings = self.env['sale.order.line'].search([('pitch_id', '=', invoice_line_obj.pitch_id.id),
                                                               ('booking_start', '=', invoice_line_obj.booking_start)])
                bookings.write({'active': False, 'booking_state': 'cancelled'})

        return super(AccountInvoice, self).invoice_validate()
