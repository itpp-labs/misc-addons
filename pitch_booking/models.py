from datetime import datetime, timedelta
import logging
import traceback
from openerp import api, models, fields, tools, SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.addons.booking_calendar.models import SLOT_START_DELAY_MINS, SLOT_DURATION_MINS

_logger = logging.getLogger(__name__)


class pitch_booking_venue(models.Model):
    _name = 'pitch_booking.venue'

    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', 'Company')


class pitch_booking_pitch(models.Model):
    _name = 'pitch_booking.pitch'
    _inherits = {'resource.resource': 'resource_id'}   
    _defaults = {
        'to_calendar': True,
    }

    venue_id = fields.Many2one('pitch_booking.venue', required=True)
    resource_id = fields.Many2one('resource.resource', ondelete='cascade', required=True)


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    venue_id = fields.Many2one('pitch_booking.venue', string='Venue', related='product_id.venue_id')
    pitch_id = fields.Many2one('pitch_booking.pitch', string='Pitch')
    resource_id = fields.Many2one('resource.resource', 'Resource', related='pitch_id.resource_id', store=True)

    @api.one
    def write(self, vals):
        result = super(sale_order_line, self).write(vals)
        if vals.get('pitch_id') and not vals.get('resource_id'):
            vals['resource_id'] = self.env['pitch_booking.pitch'].browse(vals.get('pitch_id')).resource_id
        return result

    @api.onchange('resource_id')
    def _on_change_resource(self):
        if self.resource_id:
            pitch = self.env['pitch_booking.pitch'].search([('resource_id','=',self.resource_id.id)])
            if pitch:
                self.pitch_id = pitch[0].id

    @api.onchange('pitch_id')
    def _on_change_pitch(self):
        if self.pitch_id:
            self.venue_id = self.pitch_id.venue_id.id

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(line, account_id)
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
            'resource_id': r.resource_id.id
        }

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
                    pitch_domain.append(tuple(cond));
                elif cond[0] == 'pitch_id':
                    pitch_domain.append(('name',cond[1], cond[2]));

        pitch_domain.append(('to_calendar','=',True));
        resources = self.env['pitch_booking.pitch'].search(pitch_domain)
        return resources


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    venue_id = fields.Many2one('pitch_booking.venue', string='Venue')
    pitch_id = fields.Many2one('pitch_booking.pitch', string='Pitch')
    booking_start = fields.Datetime(string="Date start")
    booking_end = fields.Datetime(string="Date end")


class product_template(models.Model):
    _inherit = 'product.template'

    venue_id = fields.Many2one('pitch_booking.venue', string='Venue')


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _add_booking_line(self, product_id, resource, start, end, tz_offset=0):
        if resource:
            for rec in self:
                line = super(sale_order, rec)._add_booking_line(product_id, resource, start, end, tz_offset)
                sol = rec.env['sale.order.line'].sudo()
                pitch_obj = rec.env['pitch_booking.pitch'].sudo()
                pitchs = pitch_obj.search([('resource_id','=',resource)], limit=1)
                if pitchs:
                    line.write({
                        'pitch_id': pitchs[0].id,
                        'venue_id': pitchs[0].venue_id.id
                    })
        return line
