# -*- coding: utf-8 -*-
import copy
from datetime import datetime, timedelta, time
import pytz
import logging

from openerp import api, models, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

from openerp.addons.resource.resource import seconds
import openerp.addons.decimal_precision as dp
from openerp.osv import fields as old_api_fields, osv

_logger = logging.getLogger(__name__)

SLOT_START_DELAY_MINS = 15
SLOT_DURATION_MINS = 60


class ResourceResource(models.Model):
    _inherit = 'resource.resource'

    to_calendar = fields.Boolean('Display on calendar')
    color = fields.Char('Color')
    has_slot_calendar = fields.Boolean('Use Working Time as Slots Definition')
    allowed_days_interval = fields.Integer(string='Allowed Days Interval', help='allow online bookings only on specified days from now')
    hours_to_prepare = fields.Integer(string='Hours to prepare', help="don't allow bookings if time before the event is less than spciefied")
    holidays_country_id = fields.Many2one(
        'res.country',
        'Holidays Country'
    )
    work_on_holidays = fields.Boolean(default=False)

    @api.multi
    def search_booking_lines(self, start, end, domain, online=False):

        bookings = self.env['sale.order.line']
        now = datetime.now()

        for r in self:
            r_domain = copy.copy(domain)
            start_dt = datetime.strptime(start, DTF)
            if online and r.hours_to_prepare:
                days = r.hours_to_prepare / 24
                hours = r.hours_to_prepare % 24
                online_min_dt = now + timedelta(days=days, hours=hours) - timedelta(minutes=now.minute, seconds=now.second)
                start_dt = start_dt if start_dt > online_min_dt else online_min_dt

            end_dt = datetime.strptime(end, DTF)
            if online and r.allowed_days_interval:
                online_max_dt = now + timedelta(days=r.allowed_days_interval) - timedelta(minutes=now.minute, seconds=now.second)
                end_dt = end_dt if end_dt < online_max_dt else online_max_dt

            r_domain.append(('resource_id', '=', r.id))
            r_domain.append(('state', '!=', 'cancel'))
            r_domain.append(('booking_end', '>=', fields.Datetime.now()))
            r_domain.append('|')
            r_domain.append('|')
            r_domain.append('&')
            r_domain.append(('booking_start', '>=', start_dt.strftime(DTF)))
            r_domain.append(('booking_start', '<', end_dt.strftime(DTF)))
            r_domain.append('&')
            r_domain.append(('booking_end', '>', start_dt.strftime(DTF)))
            r_domain.append(('booking_end', '<=', end_dt.strftime(DTF)))
            r_domain.append('&')
            r_domain.append(('booking_start', '<=', start_dt.strftime(DTF)))
            r_domain.append(('booking_end', '>=', end_dt.strftime(DTF)))

            bookings += self.env['sale.order.line'].search(r_domain)

        return bookings


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    @api.multi
    def get_working_accurate_hours(self, start_dt=None, end_dt=None):
        """
            Replacement of resource calendar method get_working_hours
            Allows to handle hour_to = 00:00
            Takes in account minutes
            Adds public holidays time (resource leaves with reason = PH)
        """
        leave_obj = self.env['resource.calendar.leaves']
        for calendar in self:
            product = self.env['product.template'].search([('calendar_id', '=', calendar.id)])
            hours = timedelta()

            day_start_dt = start_dt
            day_end_dt = end_dt
            # sometimes one booking may be on two different weekdays
            # call get_working_accurate_hours recursively for that cases
            if day_end_dt.date() == day_start_dt.date() + timedelta(1) and \
                    day_end_dt != day_end_dt.replace(hour=0, minute=0, second=0):
                    hours += timedelta(hours=self.get_working_accurate_hours(start_dt=day_end_dt.replace(hour=0, minute=0, second=0), end_dt=day_end_dt))

            weekday = [day_start_dt.weekday()]
            if product and product[0].work_on_holidays and product[0].holidays_country_id and product[0].holidays_schedule == 'premium':
                if calendar.get_attendances_for_weekdays([5]):
                    holidays = self.env['hr.holidays.public'].search([
                        ('country_id', '=', product[0].holidays_country_id.id),
                        ('year', '=', start_dt.year),
                    ], limit=1)
                    for h in holidays[0].line_ids.filtered(lambda r: r.date == start_dt.strftime(DF)):
                        weekday = [5]

            work_limits = []
            work_limits.append((day_start_dt.replace(hour=0, minute=0, second=0), day_start_dt))
            work_limits.append((day_end_dt, day_end_dt.replace(hour=23, minute=59, second=59)))

            work_dt = day_start_dt.replace(hour=0, minute=0, second=0)
            working_intervals = []
            for calendar_working_day in calendar.get_attendances_for_weekdays(weekday)[0]:
                min_from = int((calendar_working_day.hour_from - int(calendar_working_day.hour_from)) * 60)
                min_to = int((calendar_working_day.hour_to - int(calendar_working_day.hour_to)) * 60)
                x = work_dt.replace(hour=int(calendar_working_day.hour_from), minute=min_from)
                if calendar_working_day.hour_to == 0:
                    y = work_dt.replace(hour=0, minute=0) + timedelta(days=1)
                else:
                    y = work_dt.replace(hour=int(calendar_working_day.hour_to), minute=min_to)
                working_interval = (x, y)
                leaves = self.get_leave_intervals()
                leaves = leaves and self.localize_time_intervals(leaves[0])
                work_limits += leaves
                if product and not product[0].work_on_holidays and product[0].holidays_country_id:
                    holidays = self.env['hr.holidays.public'].search([
                        ('country_id', '=', product[0].holidays_country_id.id),
                        ('year', '=', start_dt.year),
                    ], limit=1)
                    for h in holidays[0].line_ids.filtered(lambda r: r.date == start_dt.strftime(DF)):
                        holiday_interval = [(datetime.combine(datetime.strptime(h.date, DF), time(0, 0)),
                                             datetime.combine(datetime.strptime(h.date, DF) + timedelta(1), time(0, 0)))]
                        holiday_interval = self.make_offset_aware(holiday_interval)
                        work_limits += holiday_interval
                work_limits = self.make_offset_aware(work_limits)
                working_interval = self.make_offset_aware([working_interval])[0]
                working_intervals += calendar.interval_remove_leaves(working_interval, work_limits)
            for interval in working_intervals:
                hours += interval[1] - interval[0]

            # Add public holidays
            leaves = leave_obj.search([('name', '=', 'PH'), ('calendar_id', '=', calendar.id)])
            leave_intervals = []
            for l in leaves:
                leave_intervals.append((datetime.strptime(l.date_from, DTF),
                                        datetime.strptime(l.date_to, DTF)
                                        ))
            clean_intervals = calendar.interval_remove_leaves((start_dt, end_dt), leave_intervals)

            for interval in clean_intervals:
                hours += (end_dt - start_dt) - (interval[1] - interval[0])

        return seconds(hours) / 3600.0

    @api.multi
    def validate_time_limits(self, booking_start, booking_end):
        # localize UTC dates to be able to compare with hours in Working Time
        tz_offset = self.env.context.get('tz_offset')
        if tz_offset:
            start_dt = datetime.strptime(booking_start, DTF) - timedelta(minutes=tz_offset)
            end_dt = datetime.strptime(booking_end, DTF) - timedelta(minutes=tz_offset)
        else:
            user_tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
            start_dt = pytz.utc.localize(fields.Datetime.from_string(booking_start)).astimezone(user_tz)
            end_dt = pytz.utc.localize(fields.Datetime.from_string(booking_end)).astimezone(user_tz)
        for calendar in self:
            hours = calendar.get_working_accurate_hours(start_dt, end_dt)
            duration = seconds(end_dt - start_dt) / 3600.0
            if round(hours, 2) != round(duration, 2):
                return False
        return True

    @api.model
    def localize_time_intervals(self, intervals):
        # localize UTC dates to be able to compare with hours in Working Time
        tz_offset = self.env.context.get('tz_offset')
        localized_intervals = []
        for interval in intervals:
            if tz_offset:
                start_dt = interval[0] - timedelta(minutes=tz_offset)
                end_dt = interval[1] - timedelta(minutes=tz_offset)
            else:
                user_tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
                start_dt = pytz.utc.localize(interval[0]).astimezone(user_tz)
                end_dt = pytz.utc.localize(interval[1]).astimezone(user_tz)
            localized_intervals.append((start_dt, end_dt))
        return localized_intervals

    @api.model
    def make_offset_aware(self, intervals):
        # some datetimes are in right timezone but without tz_info - that is from hilidays or online calendar
        # we don't need to convert them from utc to user's tz but need to append tz_info only
        # if datetimes are aware do nothing with them, if naive - append user tz
        localized_intervals = []
        for interval in intervals:
            user_tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
            start_dt = not interval[0].tzinfo and user_tz.localize(interval[0]) or interval[0]
            end_dt = not interval[1].tzinfo and user_tz.localize(interval[1]) or interval[1]
            localized_intervals.append((start_dt, end_dt))
        return localized_intervals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    resource_id = fields.Many2one('resource.resource', 'Resource')
    booking_start = fields.Datetime(string="Date start")
    booking_end = fields.Datetime(string="Date end")
    calendar_id = fields.Many2one('resource.calendar', related='product_id.calendar_id', store=True)
    project_id = fields.Many2one('account.analytic.account', compute='_compute_dependent_fields', store=False, string='Contract')
    partner_id = fields.Many2one('res.partner', compute='_compute_dependent_fields', store=False, string='Customer')
    overlap = fields.Boolean(compute='_compute_date_overlap', default=False, store=True)
    automatic = fields.Boolean(default=False, store=True, help='automatically generated booking lines')
    active = fields.Boolean(default=True)
    resource_trigger = fields.Integer(help='''we use this feild in _compute_date_overlap instead of resource_id
    because resource_id is related to pitch in pitch_booking module. If we hadn't done it then _compute_date_overlap would be called
    for each line with the same resource instead of only only for current new line''')

    @api.multi
    def write(self, vals):
        result = super(SaleOrderLine, self).write(vals)
        if vals.get('resource_id'):
            vals['resource_trigger'] = vals.get('resource_id')
        return result

    @api.multi
    def _compute_dependent_fields(self):
        for line in self:
            line.partner_id = line.order_id.partner_id
            line.project_id = line.order_id.project_id

    @api.multi
    @api.depends('resource_trigger', 'booking_start', 'booking_end', 'active')
    def _compute_date_overlap(self):
        for line in self:
            if not line.active:
                line.overlap = False
                continue
            overlaps = 0
            if line.resource_id and line.booking_start and line.booking_end:
                ids = getattr(self, '_origin', False) and self._origin.ids or bool(line.id) and [line.id] or []
                overlaps = line.search_count([('active', '=', True),
                                              '&', '|', '&', ('booking_start', '>=', line.booking_start), ('booking_start', '<', line.booking_end),
                                              '&', ('booking_end', '>', line.booking_start), ('booking_end', '<=', line.booking_end),
                                              ('resource_id', '!=', False),
                                              ('id', 'not in', ids),
                                              ('resource_id', '=', line.resource_id.id),
                                              ('state', '!=', 'cancel')])
                overlaps += line.search_count([('active', '=', True),
                                               ('id', 'not in', ids),
                                               ('booking_start', '=', line.booking_start),
                                               ('booking_end', '=', line.booking_end),
                                               ('resource_id', '=', line.resource_id.id),
                                               ('state', '!=', 'cancel')])
            line.overlap = bool(overlaps)

    @api.multi
    @api.constrains('overlap')
    def _check_overlap(self):
        for line in self:
            if line.overlap:
                overlaps_with = self.search([('active', '=', True),
                                             '&', '|', '&', ('booking_start', '>', line.booking_start), ('booking_start', '<', line.booking_end),
                                             '&', ('booking_end', '>', line.booking_start), ('booking_end', '<', line.booking_end),
                                             ('resource_id', '!=', False),
                                             ('id', '!=', line.id),
                                             ('resource_id', '=', line.resource_id.id),
                                             ('state', '!=', 'cancel')])
                overlaps_with += self.search([('active', '=', True),
                                              ('id', '!=', line.id),
                                              ('booking_start', '=', line.booking_start),
                                              ('booking_end', '=', line.booking_end),
                                              ('resource_id', '=', line.resource_id.id),
                                              ('state', '!=', 'cancel')])

                msg = 'There are bookings with overlapping times: %(this)s and %(those)s' % {'this': [line.id], 'those': overlaps_with.ids}
                raise ValidationError(msg)

    @api.multi
    @api.constrains('calendar_id', 'booking_start', 'booking_end')
    def _check_date_fit_product_calendar(self):
        for line in self.sudo():
            if line.state == 'cancel':
                continue
            if line.calendar_id and line.booking_start and line.booking_end:
                if not line.calendar_id.validate_time_limits(line.booking_start, line.booking_end):
                    raise ValidationError(_('Not valid interval of booking for the product %s.') % line.product_id.name)

    @api.multi
    @api.constrains('resource_trigger', 'booking_start', 'booking_end')
    def _check_date_fit_resource_calendar(self):
        for line in self.sudo():
            if line.state == 'cancel':
                continue
            if line.resource_id and line.resource_id.calendar_id and line.booking_start and line.booking_end:
                if not line.resource_id.calendar_id.validate_time_limits(line.booking_start, line.booking_end):
                    raise ValidationError(_('Not valid interval of booking for the resource %s.') % line.resource_id.name)

    @api.multi
    @api.constrains('booking_start')
    def _check_booking_start(self):
        for line in self:
            if not line.booking_start:
                continue
            if datetime.strptime(line.booking_start, DTF) + timedelta(minutes=SLOT_START_DELAY_MINS) < datetime.now():
                raise ValidationError(_('Please book on time in %s minutes from now.') % SLOT_START_DELAY_MINS)

    @api.multi
    @api.constrains('resource_trigger', 'booking_start', 'booking_end')
    def _check_working_time_slots(self):
        for line in self:
            user_tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
            if line.resource_id and line.resource_id.has_slot_calendar:
                resource = line.resource_id
                start_dt = datetime.strptime(line.booking_start, DTF).replace(second=0, microsecond=0)
                end_dt = datetime.strptime(line.booking_end, DTF).replace(second=0, microsecond=0)
                allowed_start = []
                allowed_end = []
                if resource.calendar_id:
                    for calendar_working_day in resource.calendar_id.get_attendances_for_weekdays([start_dt.weekday()])[0]:
                        min_from = int((calendar_working_day.hour_from - int(calendar_working_day.hour_from)) * 60)
                        min_to = int((calendar_working_day.hour_to - int(calendar_working_day.hour_to)) * 60)
                        x = start_dt.replace(hour=int(calendar_working_day.hour_from), minute=min_from)
                        user_tz.localize(x).astimezone(pytz.utc)
                        allowed_start.append(user_tz.localize(x).astimezone(pytz.utc))
                        if calendar_working_day.hour_to == 0:
                            y = start_dt.replace(hour=0, minute=0) + timedelta(days=1)
                        else:
                            y = start_dt.replace(hour=int(calendar_working_day.hour_to), minute=min_to)
                        allowed_end.append(user_tz.localize(y).astimezone(pytz.utc))
                start_dt = pytz.utc.localize(start_dt)
                end_dt = pytz.utc.localize(end_dt)
                if (start_dt not in allowed_start) or (end_dt not in allowed_end):
                    msg = "There are bookings with times outside the allowed boundary"
                    raise ValidationError(msg)

    @api.model
    def search_booking_lines(self, start, end, domain):
        domain.append(('state', '!=', 'cancel'))
        domain.append(('booking_end', '>=', fields.Datetime.now()))
        domain.append('|')
        domain.append('|')
        domain.append('&')
        domain.append(('booking_start', '>=', start))
        domain.append(('booking_start', '<', end))
        domain.append('&')
        domain.append(('booking_end', '>', start))
        domain.append(('booking_end', '<=', end))
        domain.append('&')
        domain.append(('booking_start', '<=', start))
        domain.append(('booking_end', '>=', end))
        return self.search(domain)

    @api.model
    def get_bookings(self, start, end, offset, domain, online=False):
        bookings = self.env['resource.resource'].sudo().search([]).search_booking_lines(start, end, domain, online=online)
        slot_calendar_bookings = bookings.filtered(lambda r: r.resource_id.has_slot_calendar)
        ordinary_bookings = bookings - slot_calendar_bookings
        one_hour_bookings = ordinary_bookings.filtered(lambda r: r.product_uom_qty == 1)
        many_hour_bookings = ordinary_bookings - one_hour_bookings
        res = [{
            'className': 'booked_slot resource_%s' % b.resource_id.id,
            'id': b.id,
            'title': b.resource_id.name,
            'start': '%s+00:00' % b.booking_start,
            'end': '%s+00:00' % b.booking_end,
            'resource_id': b.resource_id.id,
            'editable': False,
            'color': b.resource_id.color
        } for b in one_hour_bookings]
        for b in many_hour_bookings:
            start_dt = datetime.strptime(b.booking_start, DTF)
            end_dt = datetime.strptime(b.booking_end, DTF)
            while start_dt < end_dt:
                res.append({
                    'className': 'booked_slot resource_%s' % b.resource_id.id,
                    'id': b.id,
                    'title': b.resource_id.name,
                    'start': '%s+00:00' % start_dt.strftime(DTF),
                    'end': '%s+00:00' % (start_dt + timedelta(hours=1)).strftime(DTF),
                    'resource_id': b.resource_id.id,
                    'editable': False,
                    'color': b.resource_id.color
                })
                start_dt += timedelta(hours=1)
        for b in slot_calendar_bookings:
            start_dt = datetime.strptime(b.booking_start, DTF).replace(second=0, microsecond=0)
            start_dt_utc = pytz.utc.localize(start_dt)
            end_dt = datetime.strptime(b.booking_end, DTF).replace(second=0, microsecond=0)
            end_dt_utc = pytz.utc.localize(end_dt)
            resource = b.resource_id
            user_tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
            if resource.calendar_id:
                for calendar_working_day in resource.calendar_id.get_attendances_for_weekdays([start_dt.weekday()])[0]:
                    min_from = int((calendar_working_day.hour_from - int(calendar_working_day.hour_from)) * 60)
                    min_to = int((calendar_working_day.hour_to - int(calendar_working_day.hour_to)) * 60)
                    x = start_dt.replace(hour=int(calendar_working_day.hour_from), minute=min_from)
                    slot_start_utc = user_tz.localize(x).astimezone(pytz.utc)

                    if calendar_working_day.hour_to == 0:
                        y = start_dt.replace(hour=0, minute=0) + timedelta(days=1)
                    else:
                        y = start_dt.replace(hour=int(calendar_working_day.hour_to), minute=min_to)
                    slot_end_utc = user_tz.localize(y).astimezone(pytz.utc)

                    if slot_start_utc >= start_dt_utc and slot_end_utc <= end_dt_utc:
                        res.append({
                            'className': 'booked_slot resource_%s' % b.resource_id.id,
                            'id': b.id,
                            'title': b.resource_id.name,
                            'start': '%s+00:00' % slot_start_utc.strftime(DTF),
                            'end': '%s+00:00' % slot_end_utc.strftime(DTF),
                            'resource_id': b.resource_id.id,
                            'editable': False,
                            'color': b.resource_id.color
                        })

        return res

    @api.onchange('booking_start', 'booking_end')
    def _on_change_booking_time(self):
        domain = {'product_id': []}
        if self.venue_id:
            domain['product_id'].append(('venue_id', '=', self.venue_id.id))
        if self.booking_start and self.booking_end:
            start = datetime.strptime(self.booking_start, DTF)
            end = datetime.strptime(self.booking_end, DTF)
            self.product_uom_qty = (end - start).seconds / 3600
            booking_products = self.env['product.product'].search([('calendar_id', '!=', False)])
            domain_products = []
            domain_products = [p.id for p in booking_products
                               if p.calendar_id.validate_time_limits(self.booking_start, self.booking_end)]
            if domain_products:
                domain['product_id'].append(('id', 'in', domain_products))
        return {'domain': domain}

    @api.onchange('partner_id', 'project_id')
    def _on_change_partner(self):
        if self.order_id and self.order_id.partner_id != self.partner_id:
            self.order_id = None
        if self.order_id and self.order_id.project_id != self.project_id:
            self.order_id = None
        return self.env['sale.order'].onchange_partner_id(self.partner_id.id)

    @api.onchange('order_id')
    def _on_change_order(self):
        if self.order_id:
            self.partner_id = self.order_id.partner_id
            self.project_id = self.order_id.project_id

    @api.model
    def read_color(self, color_field):
        return self.env['resource.resource'].browse(color_field).color

    @api.model
    def create(self, values):
        if not values.get('order_id') and values.get('partner_id'):
            order_obj = self.env['sale.order']
            order_vals = order_obj.onchange_partner_id(values.get('partner_id'))['value']
            order_vals.update({
                'partner_id': values.get('partner_id'),
                'project_id': values.get('project_id')
            })
            order = order_obj.create(order_vals)
            values.update({'order_id': order.id})
        return super(SaleOrderLine, self).create(values)

    @api.onchange('product_id')
    def _on_change_product_id(self):
        if self.product_id:
            name = self.product_id.name_get()[0][1]
            if self.product_id.description_sale:
                name += '\n' + self.product_id.description_sale
            self.name = name
            warning = {}
            if self.product_id.sale_line_warn != 'no-message':
                title = _("Warning for %s") % self.product_id.name
                message = self.product_id.sale_line_warn_msg
                warning['title'] = title
                warning['message'] = message
                if self.product_id.sale_line_warn == 'block':
                    return {'value': {'product_id': False}, 'warning': warning}
                else:
                    return {'warning': warning}

    @api.onchange('product_id', 'partner_id', 'product_uom_qty')
    def _on_change_product_partner_id(self):
        if self.product_id and self.partner_id:
            pricelist = self.partner_id.property_product_pricelist
            if pricelist:
                data = self.product_id_change(pricelist.id, self.product_id.id,
                                              qty=self.product_uom_qty, partner_id=self.partner_id.id)
                for k in data['value']:
                    if k not in ['name']:
                        setattr(self, k, data['value'][k])

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
    def generate_slot(self, r, start_dt, end_dt):
        return {
            'start': start_dt.strftime(DTF),
            'end': end_dt.strftime(DTF),
            'title': r.name,
            'color': r.color,
            'className': 'free_slot resource_%s' % r.id,
            'editable': False,
            'resource_id': r.id
        }

    @api.model
    def del_booked_slots(self, slots, start, end, resources, offset, fixed_start_dt, end_dt):
        now = datetime.now() - timedelta(minutes=SLOT_START_DELAY_MINS) - timedelta(minutes=offset)
        lines = self.search_booking_lines(start, end, [('resource_id', 'in', [r['id'] for r in resources])])
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
                    del slots[l.resource_id.id][line_start_dt.strftime(DTF)]
                except:
                    _logger.warning('cannot free slot %s %s' % (
                        l.resource_id.id,
                        line_start_dt.strftime(DTF)
                    ))
                line_start_dt += timedelta(minutes=SLOT_DURATION_MINS)
        return slots

    @api.model
    def get_free_slots_resources(self, domain):
        resources = self.env['resource.resource'].search([('to_calendar', '=', True)])
        return resources

    @api.model
    def get_free_slots(self, start, end, offset, domain, online=False):
        leave_obj = self.env['resource.calendar.leaves']
        start_dt = datetime.strptime(start, DTF) - timedelta(minutes=offset)
        fixed_start_dt = start_dt
        resources = self.get_free_slots_resources(domain)
        slots = {}
        now = datetime.now() - timedelta(minutes=SLOT_START_DELAY_MINS) - timedelta(minutes=offset)
        for r in resources:
            if r.id not in slots:
                slots[r.id] = {}

            start_dt = fixed_start_dt
            if online and r.hours_to_prepare:
                days = r.hours_to_prepare / 24
                hours = r.hours_to_prepare % 24
                online_min_dt = now + timedelta(days=days, hours=hours) - timedelta(minutes=now.minute, seconds=now.second)
                start_dt = start_dt if start_dt > online_min_dt else online_min_dt

            end_dt = datetime.strptime(end, DTF) - timedelta(minutes=offset)
            if online and r.allowed_days_interval:
                online_max_dt = now + timedelta(days=r.allowed_days_interval) - timedelta(minutes=now.minute, seconds=now.second)
                end_dt = end_dt if end_dt < online_max_dt else online_max_dt

            while start_dt < end_dt:
                if start_dt < now:
                    start_dt += timedelta(minutes=SLOT_DURATION_MINS)
                    continue
                if not r.work_on_holidays and r.holidays_country_id:
                    holidays = self.env['hr.holidays.public'].search([
                        ('country_id', '=', r.holidays_country_id.id),
                        ('year', '=', start_dt.year),
                    ], limit=1)
                    if holidays[0].line_ids.filtered(lambda r: r.date == start_dt.strftime(DF)):
                        start_dt += timedelta(1)

                if r.calendar_id:
                    for calendar_working_day in r.calendar_id.get_attendances_for_weekdays([start_dt.weekday()])[0]:
                        min_from = int((calendar_working_day.hour_from - int(calendar_working_day.hour_from)) * 60)
                        min_to = int((calendar_working_day.hour_to - int(calendar_working_day.hour_to)) * 60)
                        x = start_dt.replace(hour=int(calendar_working_day.hour_from), minute=min_from)
                        if calendar_working_day.hour_to == 0:
                            y = start_dt.replace(hour=0, minute=0) + timedelta(days=1)
                        else:
                            y = start_dt.replace(hour=int(calendar_working_day.hour_to), minute=min_to)
                        if r.has_slot_calendar and x >= now and x >= start_dt and y <= end_dt:
                            slots[r.id][x.strftime(DTF)] = self.generate_slot(r, x, y)
                        elif not r.has_slot_calendar:
                            while x < y:
                                if x >= now:
                                    slots[r.id][x.strftime(DTF)] = self.generate_slot(r, x, x + timedelta(minutes=SLOT_DURATION_MINS))
                                x += timedelta(minutes=SLOT_DURATION_MINS)
                    start_dt += timedelta(days=1)
                    start_dt = start_dt.replace(hour=0, minute=0, second=0)
                else:
                    slots[r.id][start_dt.strftime(DTF)] = self.generate_slot(r, start_dt, start_dt + timedelta(minutes=SLOT_DURATION_MINS))
                    start_dt += timedelta(minutes=SLOT_DURATION_MINS)
                    continue
            leaves = leave_obj.search([('name', '=', 'PH'), ('calendar_id', '=', r.calendar_id.id)])
            for leave in leaves:
                from_dt = datetime.strptime(leave.date_from, '%Y-%m-%d %H:%M:00') - timedelta(minutes=offset)
                to_dt = datetime.strptime(leave.date_to, '%Y-%m-%d %H:%M:00') - timedelta(minutes=offset)
                if r.has_slot_calendar:
                    if from_dt >= now and from_dt >= start_dt and to_dt <= end_dt:
                        slots[r.id][from_dt.strftime(DTF)] = self.generate_slot(r, from_dt, end_dt)
                    else:
                        continue
                else:
                    from_dt = max(now, from_dt)
                    while from_dt < to_dt:
                        slots[r.id][from_dt.strftime(DTF)] = self.generate_slot(r, from_dt, from_dt + timedelta(minutes=SLOT_DURATION_MINS))
                        from_dt += timedelta(minutes=SLOT_DURATION_MINS)

        res = []
        for slot in self.del_booked_slots(slots, start, end, resources, offset, fixed_start_dt, end_dt).values():
            for pitch in slot.values():
                res.append(pitch)
        return res

    @api.multi
    def action_open_sale_order(self):
        view_id = self.env.ref('sale.view_order_form')
        order_obj = self.env['sale.order'].search([('id', '=', self.order_id.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Booking',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id.id,
            'res_id': order_obj.id,
            'res_model': 'sale.order',
            'target': 'current',
        }


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    calendar_id = fields.Many2one('resource.calendar', string='Working time')
    holidays_country_id = fields.Many2one(
        'res.country',
        'Holidays Country'
    )
    work_on_holidays = fields.Boolean(default=False)
    holidays_schedule = fields.Selection([
        ('premium', 'Premium: use Saturday weekend schedule'),
        ('promotional', 'Promotional: ordinary schedule (restrict it using leaves times if necessary)'),
        ], string='Holidays schedule', default='premium')


class SaleOrderAmountTotal(osv.osv):
    _inherit = 'sale.order'

    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        return super(SaleOrderAmountTotal, self)._amount_all_wrapper(cr, uid, ids, field_name, arg, context=None)

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_total': old_api_fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Total',
                                                store={
                                                    'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                                    'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty', 'state'], 10)},
                                                multi='sums', help="The total amount."),
    }


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.constrains('state')
    def _check_state(self):
        if self.search_count([('state', 'not in', ['draft'])]) and \
           self.env['sale.order.line'].search_count([('order_id', '=', self.id), ('overlap', '=', 'True')]):
            raise ValidationError(_('There are lines with overlap in this order. Please move overlapping lines to another time or resource'))
