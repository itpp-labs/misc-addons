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


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    venue_id = fields.Many2one('pitch_booking.venue', string='Venue')
    pitch_id = fields.Many2one('pitch_booking.pitch', string='Pitch')
    booking_start = fields.Datetime(string="Date start")
    booking_end = fields.Datetime(string="Date end")


class product_template(models.Model):
    _inherit = 'product.template'

    venue_id = fields.Many2one('pitch_booking.venue', string='Venue')


