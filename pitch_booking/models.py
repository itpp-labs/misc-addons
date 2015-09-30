from openerp import api,models,fields,tools


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
    resource_id = fields.Many2one('resource.resource')


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    venue_id = fields.Many2one('pitch_booking.venue', string='Venue')
    pitch_id = fields.Many2one('pitch_booking.pitch', string='Pitch')
    resource_id = fields.Many2one('resource.resource', related='pitch_id.resource_id', ondelete='cascade')
    start_time = fields.Datetime('Start time')
    end_time = fields.Datetime('End time')




