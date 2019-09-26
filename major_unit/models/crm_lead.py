from odoo import fields, models, api


class Lead(models.Model):
    _inherit = 'crm.lead'

    major_unit_id = fields.Many2one('major_unit.major_unit', 'Major Unit')
    major_unit_state = fields.Selection(
        [('available', 'Available'), ('sold', 'Sold')], 'State', related='major_unit_id.state')

    @api.multi
    def sale_action_quotations_new(self):
        self.ensure_one()
        # sale_deal = self.env['sale.deal'].create({})
        addr = self.partner_id.address_get(['delivery', 'invoice'])
        sale_order_vals = {
            'partner_id': self.partner_id.id,
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'details_model': 'sale.deal',
            'details_res_id': False,
            'details_model_exists': False,
            'opportunity_id': self.id,
        }
        if self.major_unit_id:
            sale_order_vals.update({
                'order_line': [(0, 0, {
                    'name': self.major_unit_id.name,
                    'product_id': self.major_unit_id.product_id.id,
                    'lot_id': self.major_unit_id.prod_lot_id.id,
                    'product_uom_qty': 1,
                    'product_uom': self.major_unit_id.product_id.uom_id.id,
                })]
            })
        sale_order = self.env['sale.order'].create(sale_order_vals)
        # if not sale_order.sale_deal_id and sale_order.details_model == 'sale.deal':
        #     # in some cases, for example create&edit, sale_order_id is not written to the deal automatically
        #     sale_deal.write({
        #         'sale_order_id': sale_order.id,
        #     })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'target': 'current',
            'res_id': sale_order.id
        }
