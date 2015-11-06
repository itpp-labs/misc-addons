from datetime import datetime, timedelta
import pytz

from openerp import api, models, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

SLOT_START_DELAY_MINS = 15


class resource_resource(models.Model):
    _inherit = 'resource.resource'

    to_calendar = fields.Boolean('Display on calendar')
    color = fields.Char('Color')


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    resource_id = fields.Many2one('resource.resource', 'Resource')
    booking_start = fields.Datetime(string="Date start")
    booking_end = fields.Datetime(string="Date end")
    calendar_id = fields.Many2one('resource.calendar', related='product_id.calendar_id')

    @api.multi
    @api.constrains('resource_id', 'booking_start', 'booking_end')
    def _check_date_overlap(self):
        for line in self:
            if line.state == 'cancel':
                continue
            if line.resource_id and line.booking_start and line.booking_end:
                overlaps = line.search_count(['&','|','&',('booking_start', '>', line.booking_start), ('booking_start', '<', line.booking_end),
                                              '&',('booking_end', '>', line.booking_start), ('booking_end', '<', line.booking_end),
                                              ('id', '!=', line.id),
                                              ('resource_id', '!=', False),
                                              ('resource_id', '=', line.resource_id.id),
                                              ('state', '!=', 'cancel')
                ])
                overlaps += line.search_count([('id', '!=', line.id),
                                               ('booking_start', '=', line.booking_start),
                                               ('booking_end', '=', line.booking_end),
                                               ('resource_id', '=', line.resource_id.id),
                                               ('state', '!=', 'cancel')
                ])
                if overlaps:
                    raise ValidationError('There already is booking at that time.')

    @api.multi
    @api.constrains('calendar_id', 'booking_start', 'booking_end')
    def _check_date_fit_product_calendar(self):
        for line in self.sudo():
            if line.state == 'cancel':
                continue
            if line.calendar_id and line.booking_start and line.booking_end:
                if not line.validate_time_limits(line.calendar_id.id, line.booking_start, line.booking_end):
                    raise ValidationError(_('Not valid interval of booking for the product %s.') % line.product_id.name)

    @api.multi
    @api.constrains('booking_start')
    def _check_booking_start(self):
        for line in self:
            if not line.booking_start:
                continue
            if datetime.strptime(line.booking_start, DTF) - timedelta(minutes=SLOT_START_DELAY_MINS) < datetime.now():
                raise ValidationError(_('Please book at least in %s minutes from now.') % SLOT_START_DELAY_MINS)

    @api.model
    def validate_time_limits(self, calendar_id, booking_start, booking_end):
        calendar_obj = self.env['resource.calendar']
        leave_obj = self.env['resource.calendar.leaves']
        user_tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
        start_dt = pytz.utc.localize(fields.Datetime.from_string(booking_start)).astimezone(user_tz)
        end_dt = pytz.utc.localize(fields.Datetime.from_string(booking_end)).astimezone(user_tz)
        hours = calendar_obj.browse(calendar_id).get_working_hours(start_dt, end_dt)
        if not hours:
            return False
        else:
            hours = hours[0]
        duration = (end_dt - start_dt).seconds/3600
        if hours != duration:
            leaves = leave_obj.search([('name','=','PH'), ('calendar_id','=',calendar_id)])
            leave_intervals = []
            for l in leaves:
                leave_intervals.append((datetime.strptime(l.date_from, DTF),
                                        datetime.strptime(l.date_to, DTF)
                ))
            clean_intervals = calendar_obj.interval_remove_leaves((start_dt, end_dt), leave_intervals)
            hours += duration
            for interval in clean_intervals:
                hours -= (interval[1] - interval[0]).seconds/3600
            if hours != duration:
                return False
        return True

    @api.model
    def get_bookings(self, start, end, resource_ids):
        domain  = [
            ('booking_start', '>=', start),
            ('booking_end', '<=', end),
            ('booking_start', '>=', fields.Datetime.now()),
            ('state', '!=', 'cancel')
            ]
        if resource_ids:
            domain.append(('resource_id', 'in', resource_ids))
        bookings = self.sudo().search(domain)
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
        if self.booking_start and self.booking_end:
            start = datetime.strptime(self.booking_start, DTF)
            end = datetime.strptime(self.booking_end, DTF)
            self.product_uom_qty = (end - start).seconds/3600


class product_template(models.Model):
    _inherit = 'product.template'

    calendar_id = fields.Many2one('resource.calendar', string='Working time')
