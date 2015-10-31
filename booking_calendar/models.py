from datetime import datetime
import pytz

from openerp import api, models, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.exceptions import ValidationError


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

    @api.one
    @api.constrains('resource_id', 'booking_start', 'booking_end')
    def _check_date_overlap(self):
        if self.resource_id and self.booking_start and self.booking_end:
            overlaps = self.search_count(['&','|','&',('booking_start', '>', self.booking_start), ('booking_start', '<', self.booking_end),
                                          '&',('booking_end', '>', self.booking_start), ('booking_end', '<', self.booking_end),
                                          ('id', '!=', self.id),
                                          ('resource_id', '!=', False),
                                          ('resource_id', '=', self.resource_id.id)
            ])
            overlaps += self.search_count([('id', '!=', self.id),
                                           ('booking_start', '=', self.booking_start),
                                           ('booking_end', '=', self.booking_end),
                                           ('resource_id', '=', self.resource_id.id)])
            if overlaps:
                raise ValidationError('There already is booking at that time.')

    @api.multi
    @api.constrains('calendar_id', 'booking_start', 'booking_end')
    def _check_date_fit_product_calendar(self):
        for record in self:
            if record.calendar_id and record.booking_start and record.booking_end:
                is_valid = self.validate_time_limits(record.calendar_id.id, record.booking_start, record.booking_end)
                if not is_valid:
                    raise ValidationError('Not valid interval of booking for the product %s.' % self.product_id.name)

    @api.model
    def validate_time_limits(self, calendar_id, booking_start, booking_end):
        calendar_obj = self.env['resource.calendar']
        leave_obj = self.env['resource.calendar.leaves']
        user_tz = pytz.timezone(self.env.context.get('tz', 'UTC'))
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


class product_template(models.Model):
    _inherit = 'product.template'

    calendar_id = fields.Many2one('resource.calendar', string='Working time')
