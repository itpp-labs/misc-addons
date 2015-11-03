import traceback

from openerp import api, models, fields, tools, SUPERUSER_ID


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

    @api.onchange('resource_id')
    def _on_change_resource(self):
        if self.resource_id:
            pitch = self.env['pitch_booking.pitch'].search([('resource_id','=',self.resource_id.id)])
            if pitch:
                self.pitch_id = pitch[0].id

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
    def _add_booking_line(self, product_id, resource, start, end):
        if resource:
            for rec in self:
                line = super(sale_order, rec)._add_booking_line(product_id, resource, start, end)
                sol = rec.env['sale.order.line'].sudo()
                pitch_obj = rec.env['pitch_booking.pitch'].sudo()
                pitchs = pitch_obj.search([('resource_id','=',resource)], limit=1)
                if pitchs:
                    line.write({
                        'pitch_id': pitchs[0].id,
                        'venue_id': pitchs[0].venue_id.id
                    })
        return line