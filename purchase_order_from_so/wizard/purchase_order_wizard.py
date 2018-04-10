from odoo import models, fields, api, _


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
