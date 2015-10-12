from datetime import datetime

from openerp import api, models, fields, SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import ValidationError



class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    calendar_id = fields.Many2one('resource.calendar', related='product_id.calendar_id')

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
        start_dt = datetime.strptime(booking_start, DEFAULT_SERVER_DATETIME_FORMAT)
        end_dt = datetime.strptime(booking_end, DEFAULT_SERVER_DATETIME_FORMAT)
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
                leave_intervals.append((datetime.strptime(l.date_from, DEFAULT_SERVER_DATETIME_FORMAT),
                                        datetime.strptime(l.date_to, DEFAULT_SERVER_DATETIME_FORMAT)
                ))
            clean_intervals = calendar_obj.interval_remove_leaves((start_dt, end_dt), leave_intervals)
            hours += duration
            for interval in clean_intervals:
                hours -= (interval[1] - interval[0]).seconds/3600
            if hours != duration:
                return False
        return True


class product_template(models.Model):
    _inherit = 'product.template'

    calendar_id = fields.Many2one('resource.calendar', string='Working time')
