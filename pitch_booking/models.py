# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import pytz
import logging
from openerp import api
from openerp import fields
from openerp import models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.addons.booking_calendar.models import SLOT_START_DELAY_MINS, SLOT_DURATION_MINS
from openerp.addons.base.res.res_partner import _tz_get

_logger = logging.getLogger(__name__)

SLOT_START_DELAY_MINS = 15
SLOT_DURATION_MINS = 60


class PitchBookingVenue(models.Model):
    _name = 'pitch_booking.venue'

    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', 'Company')
    tz = fields.Selection(_tz_get, 'Timezone', default=lambda r: r.env.context.get('tz'))
    tz_offset = fields.Integer(compute='_compute_tz_offset')

    @api.multi
    def _compute_tz_offset(self):
        for record in self:
            venue_now = datetime.now(pytz.timezone(record.tz or record.env.context.get('tz')))
            record.tz_offset = venue_now.utcoffset().total_seconds()/60

    @api.multi
    def localize(self, time_string_in_utc):
        self.ensure_one()
        venue_tz = pytz.timezone(self.tz)
        time_obj = fields.Datetime.from_string(time_string_in_utc)
        time_obj = pytz.utc.localize(time_obj).astimezone(venue_tz)
        time_str_venue_tz = time_obj.strftime(DTF)
        return time_str_venue_tz


class PitchBookingPitch(models.Model):
    _name = 'pitch_booking.pitch'
    _inherits = {'resource.resource': 'resource_id'}
    _defaults = {
        'to_calendar': True,
    }

    venue_id = fields.Many2one('pitch_booking.venue', required=True)
    resource_id = fields.Many2one('resource.resource', ondelete='cascade', required=True)

    @api.model
    def generate_slot(self, start_dt, end_dt, online=False, offset=0, calendar=False):
        self.ensure_one()
        start_str = start_dt.strftime(DTF)
        end_str = end_dt.strftime(DTF)
        venue = self.venue_id
        return {
            'start': online and not calendar and venue.localize(start_str) or start_str,
            'end': online and not calendar and venue.localize(end_str) or end_str,
            'title': self.name,
            'color': self.color,
            'className': 'free_slot resource_%s' % self.id,
            'editable': False,
            'resource_id': self.resource_id.id
        }

    @api.multi
    def interval_available_slots(self, start, end, offset, online=False):
        self.ensure_one()
        slots = {}
        # offset is 0 if slots request comes from online calendar

        # datetime.now() is in UTC inside odoo
        now = datetime.now() \
            - timedelta(minutes=SLOT_START_DELAY_MINS) \
            - timedelta(minutes=offset) \
            + timedelta(hours=1)
        now = now.replace(minute=0, second=0)
        start_dt = datetime.strptime(start, DTF) - timedelta(minutes=offset)
        is_current_week = False
        if start_dt < now:
            is_current_week = True
            start_dt = now
        end_dt = datetime.strptime(end, DTF) - timedelta(minutes=offset)
        if online: # online fullcalendar initialized with timezone=false now, backend calendar has 'local' timezone by default

            # the difference between them is that backend calendar takes slots in utc and localizes them (using system timezone settings)
            # online calendar in its turn doesn't localize slots but expects them in proper timezone (that is from venue)

            # for online we should shift start so that after localization it would be from 00:00 for future weeks
            # and now for current week
            # (we localize online slots before place them on calendar in self.generate_slot)
            if not is_current_week:
                start_dt = start_dt - timedelta(minutes=self.venue_id.tz_offset)
            end_dt = end_dt - timedelta(minutes=self.venue_id.tz_offset)

        if online and self.hours_to_prepare:
            online_min_dt = now + timedelta(hours=self.hours_to_prepare)
            start_dt = start_dt if start_dt > online_min_dt else online_min_dt

        if online and self.allowed_days_interval:
            online_max_dt = now + timedelta(days=self.allowed_days_interval)
            end_dt = end_dt if end_dt < online_max_dt else online_max_dt

        while start_dt < end_dt:
            start_d = online and \
                (start_dt + timedelta(minutes=self.venue_id.tz_offset)).date() or \
                start_dt.date()

            if not self.work_on_holidays and self.holidays_country_id:
                holidays = self.env['hr.holidays.public'].search([
                    ('country_id', '=', self.holidays_country_id.id),
                    ('year', '=', start_d.year),
                ], limit=1)
                if holidays[0].line_ids.filtered(lambda r: r.date == start_d.strftime(DF)):
                    start_dt += timedelta(1)

            if self.calendar_id:
                for attendance in self.calendar_id.get_attendances_for_weekdays([start_d.weekday()])[0]:
                    min_from = int((attendance.hour_from - int(attendance.hour_from)) * 60)
                    min_to = int((attendance.hour_to - int(attendance.hour_to)) * 60)

                    x = datetime.combine(start_d, datetime.min.time().replace(hour=int(attendance.hour_from), minute=min_from))
                    if attendance.hour_to == 0:
                        y = datetime.combine(start_d, datetime.min.time()) + timedelta(1)
                    else:
                        y = datetime.combine(start_d, datetime.min.time().replace(hour=int(attendance.hour_to), minute=min_to))
                    if self.has_slot_calendar and x >= now and x >= start_dt and y <= end_dt:
                        slots[x.strftime(DTF)] = self.generate_slot(x, y, online=online, offset=offset, calendar=True)
                    elif not self.has_slot_calendar:
                        while x < y:
                            if x >= now:
                                slots[x.strftime(DTF)] = self.generate_slot(x,
                                                                            x + timedelta(minutes=SLOT_DURATION_MINS),
                                                                            online=online,
                                                                            offset=offset,
                                                                            calendar=True)
                            x += timedelta(minutes=SLOT_DURATION_MINS)
                start_dt += timedelta(1)
                start_dt = start_dt.replace(hour=0, minute=0, second=0)
            else:
                slots[start_dt.strftime(DTF)] = self.generate_slot(start_dt, start_dt + timedelta(minutes=SLOT_DURATION_MINS), online=online, offset=offset)
                start_dt += timedelta(minutes=SLOT_DURATION_MINS)

        return slots


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    venue_id = fields.Many2one('pitch_booking.venue', string='Venue', related='product_id.venue_id')
    pitch_id = fields.Many2one('pitch_booking.pitch', string='Pitch')
    resource_id = fields.Many2one('resource.resource', 'Resource', related='pitch_id.resource_id', store=True)

    @api.onchange('resource_id')
    def _on_change_resource(self):
        if self.resource_id:
            pitch = self.env['pitch_booking.pitch'].search([('resource_id', '=', self.resource_id.id)])
            if pitch:
                self.pitch_id = pitch[0].id

    @api.onchange('pitch_id')
    def _on_change_pitch(self):
        if self.pitch_id:
            self.venue_id = self.pitch_id.venue_id.id

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        res = super(SaleOrderLine, self)._prepare_order_line_invoice_line(line, account_id)
        res.update({
            'venue_id': line.venue_id.id,
            'pitch_id': line.pitch_id.id,
            'booking_start': line.booking_start,
            'booking_end': line.booking_end
        })
        return res

    @api.model
    def get_resources(self, venue_id, pitch_id):
        pitch_obj = self.env['pitch_booking.pitch'].sudo()
        venue_obj = self.env['pitch_booking.venue'].sudo()
        if not venue_id:
            venues = venue_obj.search([])
            venue_id = venues[0].id if venues else None
        resources = []
        if pitch_id:
            resources = [pitch_obj.browse(int(pitch_id)).resource_id]
        elif venue_id:
            resources = [p.resource_id for p in pitch_obj.search([('venue_id', '=', int(venue_id))])]
        return [{
            'name': r.name,
            'id': r.id,
            'color': r.color
        } for r in resources]

    @api.model
    def del_booked_slots(self, slots, start, end, resources, offset, fixed_start_dt, end_dt):
        now = datetime.now() - timedelta(minutes=SLOT_START_DELAY_MINS) - timedelta(minutes=offset)
        lines = self.search_booking_lines(start, end, [('pitch_id', 'in', [r['id'] for r in resources])])
        for l in lines:
            line_start_dt = datetime.strptime(l.booking_start, '%Y-%m-%d %H:%M:00') - timedelta(minutes=offset)
            line_start_dt -= timedelta(minutes=divmod(line_start_dt.minute, SLOT_DURATION_MINS)[1])
            line_end_dt = datetime.strptime(l.booking_end, DTF) - timedelta(minutes=offset)
            while line_start_dt < line_end_dt:
                if line_start_dt >= end_dt:
                    break
                elif line_start_dt < fixed_start_dt or line_start_dt < now:
                    line_start_dt += timedelta(minutes=SLOT_DURATION_MINS)
                    continue
                try:
                    del slots[l.pitch_id.id][line_start_dt.strftime(DTF)]
                except:
                    _logger.warning('cannot free slot %s %s' % (
                        l.pitch_id.id,
                        line_start_dt.strftime(DTF)
                    ))
                line_start_dt += timedelta(minutes=SLOT_DURATION_MINS)
        return slots

    @api.model
    def get_free_slots_resources(self, domain):
        pitch_domain = []
        for cond in domain:
            if type(cond) in (tuple, list):
                if cond[0] == 'venue_id':
                    pitch_domain.append(tuple(cond))
                elif cond[0] == 'pitch_id':
                    pitch_domain.append(('name', cond[1], cond[2]))

        pitch_domain.append(('to_calendar', '=', True))
        resources = self.env['pitch_booking.pitch'].search(pitch_domain)
        return resources

    @api.model
    def get_booking_available_products(self, event, products):
        products = super(SaleOrderLine, self).get_booking_available_products(event, products)
        res = []
        pitch = self.env['pitch_booking.pitch'].search([('resource_id', '=', int(event['resource']))])
        if pitch and pitch.venue_id:
            res = products.filtered(lambda p: p.venue_id == pitch.venue_id)
        return res

    @api.multi
    def localize_to_online(self, time_string_in_utc):
        # online calendar should have the setting as follows
        # timezone: false
        # you don't store timezone information for your events and you want all events to render consistently across all client computers, regardless of timezone
        # online customers may book from everywhere but venues are always in certain timezone. Show online slots in venue tz therefore
        self.ensure_one()
        return self.venue_id.localize(time_string_in_utc)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    _order = "booking_start,invoice_id,sequence,id"

    venue_id = fields.Many2one('pitch_booking.venue', string='Venue')
    pitch_id = fields.Many2one('pitch_booking.pitch', string='Pitch')
    booking_start = fields.Datetime(string="Date start")
    booking_end = fields.Datetime(string="Date end")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    venue_id = fields.Many2one('pitch_booking.venue', string='Venue')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _add_booking_line(self, product_id, resource, start, end, tz_offset=0):
        if resource:
            for rec in self:
                line = super(SaleOrder, rec)._add_booking_line(product_id, resource, start, end, tz_offset)
                pitch_obj = rec.env['pitch_booking.pitch'].sudo()
                pitchs = pitch_obj.search([('resource_id', '=', resource)], limit=1)
                if pitchs:
                    line.write({
                        'pitch_id': pitchs[0].id,
                        'venue_id': pitchs[0].venue_id.id
                    })
        return line
