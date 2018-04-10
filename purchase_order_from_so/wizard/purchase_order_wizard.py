from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class PurchaseOrderWizard(models.TransientModel):
    _name = 'purchase.order.wizard'
    _description = 'Generate Purchase Order from Sale Order'

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, change_default=True)
    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    date_order = fields.Datetime('Order Date', required=True, index=True, copy=False, default=fields.Datetime.now,
                                 help="Depicts the date where the Quotation should be validated and converted into a purchase order.")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', required=True,
                                      help="This will determine operation type of incoming shipment")
    order_line = fields.One2many('purchase.order.line.wizard', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)


    def create_po_from_so(self, s_order):
        p_lines = []
        for line in s_order.order_line:
            p_line = self.env['purchase.order.line.wizard'].create({
                'name': line.name,
                'product_qty': line.product_uom_qty,
                'date_planned': line.order_id.date_order,
                'product_uom': line.product_uom.id,
                'product_id': line.product_id.id,
                'price_unit': line.price_unit,
                'order_id': line.order_id.id,
            })
            p_lines.append(p_line.id)

        return {
            'partner_id': s_order.partner_id.id,
            'date_order': s_order.date_order,
            'currency_id': s_order.currency_id.id,
            'company_id': s_order.company_id.id,
            # 'picking_type_id': self.company_id.street,
            'order_line': p_lines,
        }


class PurchaseOrderLineWizard(models.TransientModel):
    _name = 'purchase.order.line.wizard'
    _description = 'Purchase Order Lines'

    name = fields.Text(string='Description', required=True)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    date_planned = fields.Datetime(string='Scheduled Date', required=True, index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))

    # price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    # price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    # price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    order_id = fields.Many2one('purchase.order.wizard', string='Order Reference', index=True, required=True, ondelete='cascade')

