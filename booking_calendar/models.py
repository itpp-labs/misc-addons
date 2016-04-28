from datetime import datetime, timedelta
import pytz
from dateutil import rrule
import logging

from openerp import api, models, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

from openerp.addons.resource.resource import seconds
import openerp.addons.decimal_precision as dp
from openerp.osv import fields as old_api_fields, osv

_logger = logging.getLogger(__name__)

SLOT_START_DELAY_MINS = 15
SLOT_DURATION_MINS = 60


class resource_resource(models.Model):
    _inherit = 'resource.resource'

    to_calendar = fields.Boolean('Display on calendar')
    color = fields.Char('Color')
    has_slot_calendar = fields.Boolean('Use Working Time as Slots Definition')


class resource_calendar(models.Model):
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
            id = calendar.id
            hours = timedelta()
            for day in rrule.rrule(rrule.DAILY, dtstart=start_dt,
                                   until=end_dt.replace(hour=23, minute=59, second=59),
                                   byweekday=calendar.get_weekdays()[0]):
                day_start_dt = day.replace(hour=0, minute=0, second=0)
                if start_dt and day.date() == start_dt.date():
                    day_start_dt = start_dt
                day_end_dt = day.replace(hour=23, minute=59, second=59)
                if end_dt and day.date() == end_dt.date():
                    day_end_dt = end_dt
                work_limits = []
                work_limits.append((day_start_dt.replace(hour=0, minute=0, second=0), day_start_dt))
                work_limits.append((day_end_dt, day_end_dt.replace(hour=23, minute=59, second=59)))

                intervals = []
                work_dt = day_start_dt.replace(hour=0, minute=0, second=0)
                working_intervals = []
                for calendar_working_day in calendar.get_attendances_for_weekdays([day_start_dt.weekday()])[0]:
                    min_from = int((calendar_working_day.hour_from - int(calendar_working_day.hour_from)) * 60)
                    min_to = int((calendar_working_day.hour_to - int(calendar_working_day.hour_to)) * 60)
                    x = work_dt.replace(hour=int(calendar_working_day.hour_from), minute=min_from)
                    if calendar_working_day.hour_to == 0:
                        y = work_dt.replace(hour=0, minute=0)+timedelta(days=1)
                    else:
                        y = work_dt.replace(hour=int(calendar_working_day.hour_to), minute=min_to)
                    working_interval = (x, y)
                    working_intervals += calendar.interval_remove_leaves(working_interval, work_limits)
                for interval in working_intervals:
                    hours += interval[1] - interval[0]

            #Add public holidays
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
        #localize UTC dates to be able to compare with hours in Working Time
        user_tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
        start_dt = pytz.utc.localize(fields.Datetime.from_string(booking_start)).astimezone(user_tz)
        end_dt = pytz.utc.localize(fields.Datetime.from_string(booking_end)).astimezone(user_tz)
        for calendar in self:
            hours = calendar.get_working_accurate_hours(start_dt, end_dt)
            duration = seconds(end_dt - start_dt) / 3600.0
            if round(hours, 2) != round(duration, 2):
                return False
        return True


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    resource_id = fields.Many2one('resource.resource', 'Resource')
    booking_start = fields.Datetime(string="Date start")
    booking_end = fields.Datetime(string="Date end")
    calendar_id = fields.Many2one('resource.calendar', related='product_id.calendar_id')
    project_id = fields.Many2one('account.analytic.account', compute='_compute_dependent_fields', store=False, string='Contract')
    partner_id = fields.Many2one('res.partner', compute='_compute_dependent_fields', store=False, string='Customer')
    overlap = fields.Boolean(compute='_compute_date_overlap', default=False, store=True)
    automatic = fields.Boolean(default=False, store=True, help='automatically generated booking lines')
    active = fields.Boolean(default=True)
    resource_trigger = fields.Integer(help='''we use this feild in _compute_date_overlap instead of resource_id
    because resource_id is related to pitch in pitch_booking module. If we hadn't done it then _compute_date_overlap would be called
    for each line with the same resource instead of only only for current new line''')

    @api.one
    def write(self, vals):
        result = super(sale_order_line, self).write(vals)
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
    def get_bookings(self, start, end, resource_ids):
        domain = []
        if resource_ids:
            domain.append(('resource_id', 'in', resource_ids))
        bookings = self.sudo().search_booking_lines(start, end, domain)
        return [{
            'id': b.id,
            'title': b.resource_id.name,
            'start': '%s+00:00' % b.booking_start,
            'end': '%s+00:00' % b.booking_end,
            'resourceId': b.resource_id.id,
            'editable': False,
            'color': b.resource_id.color
        } for b in bookings]

    @api.onchange('booking_start', 'booking_end')
    def _on_change_booking_time(self):
        domain = {'product_id': []}
        if self.venue_id:
            domain['product_id'].append(('venue_id', '=', self.venue_id.id))
        if self.booking_start and self.booking_end:
            start = datetime.strptime(self.booking_start, DTF)
            end = datetime.strptime(self.booking_end, DTF)
            self.product_uom_qty = (end - start).seconds/3600
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
        if not values.get('order_id') and  values.get('partner_id'):
            order_obj = self.env['sale.order']
            order_vals = order_obj.onchange_partner_id(values.get('partner_id'))['value']
            order_vals.update({
                'partner_id': values.get('partner_id'),
                'project_id': values.get('project_id')
            })
            order = order_obj.create(order_vals)
            values.update({'order_id': order.id})
        return super(sale_order_line, self).create(values)

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
                    if not k in ['name']:
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
            resources = [p.resource_id for p in pitch_obj.search([('venue_id','=',int(venue_id))])]
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
        resources = self.env['resource.resource'].search([('to_calendar','=',True)])
        return resources

    @api.model
    def get_free_slots(self, start, end, offset, domain):
        leave_obj = self.env['resource.calendar.leaves']
        start_dt = datetime.strptime(start, DTF) - timedelta(minutes=offset)
        end_dt = datetime.strptime(end, DTF) - timedelta(minutes=offset)
        fixed_start_dt = start_dt
        resources = self.get_free_slots_resources(domain)
        slots = {}
        now = datetime.now() - timedelta(minutes=SLOT_START_DELAY_MINS) - timedelta(minutes=offset)
        for r in resources:
            if not r.id in slots:
                slots[r.id] = {}
            start_dt = fixed_start_dt
            while start_dt < end_dt:
                if start_dt < now:
                    start_dt += timedelta(minutes=SLOT_DURATION_MINS)
                    continue
                if r.calendar_id:
                    for calendar_working_day in r.calendar_id.get_attendances_for_weekdays([start_dt.weekday()])[0]:
                        min_from = int((calendar_working_day.hour_from - int(calendar_working_day.hour_from)) * 60)
                        min_to = int((calendar_working_day.hour_to - int(calendar_working_day.hour_to)) * 60)
                        x = start_dt.replace(hour=int(calendar_working_day.hour_from), minute=min_from)
                        if calendar_working_day.hour_to == 0:
                            y = start_dt.replace(hour=0, minute=0)+timedelta(days=1)
                        else:
                            y = start_dt.replace(hour=int(calendar_working_day.hour_to), minute=min_to)
                        if r.has_slot_calendar and x >= now and x >= start_dt and y <= end_dt:
                            slots[r.id][x.strftime(DTF)] = self.generate_slot(r, x, y)
                        elif not r.has_slot_calendar:
                            while x < y:
                                if x >= now:
                                    slots[r.id][x.strftime(DTF)] = self.generate_slot(r, x, x+timedelta(minutes=SLOT_DURATION_MINS))
                                x += timedelta(minutes=SLOT_DURATION_MINS)
                    start_dt += timedelta(days=1)
                    start_dt = start_dt.replace(hour=0, minute=0, second=0)
                else:
                    slots[r.id][start_dt.strftime(DTF)] = self.generate_slot(r, start_dt, start_dt+timedelta(minutes=SLOT_DURATION_MINS))
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
                        slots[r.id][from_dt.strftime(DTF)] = self.generate_slot(r, from_dt, from_dt+timedelta(minutes=SLOT_DURATION_MINS))
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


class product_template(models.Model):
    _inherit = 'product.template'

    calendar_id = fields.Many2one('resource.calendar', string='Working time')


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
                                                    'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty', 'state'], 10),
                                                },
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
