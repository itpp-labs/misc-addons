from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.exceptions import Warning


class CustomerCreateRides(models.TransientModel):
    _name = "res.partner.create.vehicles"
    _description = "create ride"

    vin_sn = fields.Char('Vin No.')
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    product_id = fields.Many2one(
        'product.product', 'My ride', domain="[('details_model','=','vehicle')]")

    @api.model
    def default_get(self, fields):
        res = super(CustomerCreateRides, self).default_get(fields)
        if not res.get('partner_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'res.partner':
            res['partner_id'] = self.env['res.partner'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).id
        return res

    def _prepare_ride(self, product):
        res = {
            'name': product.name or None,
            'image': product.image or None,
          
        }
        return res

    @api.multi
    def create_from_existing(self):
        """ Create ride from existing product"""
        if not self.vin_sn:
            raise Warning(_('Please enter vin no of new vehicle'))

        my_ride_details = self._prepare_ride(self.product_id)
        my_ride_details['vin_sn'] = self.vin_sn
        my_ride_details['partner_id'] = self.partner_id.id
        my_ride_details['prod_lot_id'] = self.env['stock.production.lot'].create(
            {'product_id': self.product_id.id, 'name': self.vin_sn}).id
        vehicle = self.env['major_unit.major_unit'].create(
            my_ride_details)
        return {'type': 'ir.actions.act_window_close'}

    def create_new(self):
        context = dict(self._context or {})
        context['partner_id'] = self.partner_id.id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'major_unit.major_unit',
            'context': context,
        }
