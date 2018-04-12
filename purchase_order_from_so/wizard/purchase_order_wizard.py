# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class PurchaseOrderWizard(models.TransientModel):
    _name = 'purchase.order.wizard'
    _description = 'Generate Purchase Order from Sale Order'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True)
    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    date_order = fields.Datetime('Order Date', required=True, index=True, copy=False, default=fields.Datetime.now,
                                 help="Depicts the date where the Quotation should be validated and converted into a purchase order.")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)
    order_line_ids = fields.One2many('purchase.order.line.wizard', 'order_id', string='Order Lines', copy=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True,
                                    help="Not empty if an origin for purchase order was sale order")

    def create_purchase_orders(self):
        po_env = self.env['purchase.order']
        vendor_ids = map(lambda x: x.partner_id.id, self.order_line_ids)
        for ven in vendor_ids:
            p_order = po_env.search([('partner_id', '=', ven),
                                     ('customer_id', '=', self.partner_id.id),
                                     ('sale_order_id', '=', self.sale_order_id.id)])
            if len(p_order):
                p_order = p_order[0]
                p_order.write({
                    'name': self.name,
                    'date_order': self.date_order,
                    'currency_id': self.currency_id.id,
                })
            else:
                p_order = po_env.create({
                    'name': self.name,
                    'date_order': self.date_order,
                    'partner_id': ven,
                    'currency_id': self.currency_id.id,
                    'sale_order_id': self.sale_order_id.id,
                    'customer_id': self.partner_id.id,
                    'order_line': [(5, 0, 0)],
                })
            for line in self.order_line_ids.filtered(lambda l: l.partner_id.id == ven):
                o_line = self.env['purchase.order.line'].create({
                    'name': line.name,
                    'product_qty': line.product_qty_to_order,
                    'date_planned': line.date_planned,
                    'order_id': p_order.id,
                    'product_uom': line.product_uom.id,
                    'product_id': line.product_id.id,
                    'price_unit': line.purchase_price,
                    'taxes_id': line.taxes_id.ids,
                })
                p_order.write({
                    'order_line': [(4, o_line.id)]
                })

    def create_po_lines_from_so(self, s_order):
        for line in s_order.order_line:
            product = self.env['product.product'].browse(line.product_id.id)
            qty_available = product.qty_available
            mto_id = self.env['stock.location.route'].search([('name', 'like', _('Make To Order'))], limit=1).id
            mto_product = mto_id in product.product_tmpl_id.route_ids.ids
            partner_id = False
            vendors = product.product_tmpl_id.seller_ids
            if len(vendors):
                partner_id = vendors[0].name.id
            p_line = self.env['purchase.order.line.wizard'].create({
                'name': line.name,
                'product_qty_sold': line.product_uom_qty,
                'product_qty_to_order': max(line.product_uom_qty - qty_available, 0),
                'date_planned': line.order_id.date_order,
                'product_uom': line.product_uom.id,
                'product_id': product.id,
                'order_id': self.id,
                'partner_id': partner_id,
                'mto_product': mto_product,
                'purchase_price': product.standard_price,
                'taxes_id': line.tax_id.id,
            })
            self.order_line_ids += p_line


class PurchaseOrderLineWizard(models.TransientModel):
    _name = 'purchase.order.line.wizard'
    _description = 'Purchase Order Lines'

    name = fields.Text(string='Description', required=True)
    product_qty_sold = fields.Float(string='Quantity Sold', digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_qty_to_order = fields.Float(string='Quantity to Order', digits=dp.get_precision('Product Unit of Measure'))
    date_planned = fields.Datetime(string='Order Date', required=True, index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor')
    order_id = fields.Many2one('purchase.order.wizard', string='Order Reference', index=True, required=True, ondelete='cascade')
    mto_product = fields.Boolean(string="MTO", help="Make To Order product")
    purchase_price = fields.Float('Unit Cost', digits=dp.get_precision('Product Price'),
                                  help="Cost used for stock valuation. Also used as a base price for pricelists. "
                                       "Expressed in the default unit of measure of the product.")
    total_price = fields.Float(compute="_compute_total_price", string='Total Price', digits=dp.get_precision('Product Price'))
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])

    @api.depends('product_qty_to_order', 'purchase_price', 'taxes_id')
    def _compute_total_price(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.purchase_price, line.order_id.currency_id, line.product_qty_to_order, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'total_price': taxes['total_included'],
            })
