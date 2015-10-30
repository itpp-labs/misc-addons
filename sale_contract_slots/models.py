# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProductTemplateSlots(models.Model):
    _inherit = 'product.template'

    slots = fields.Integer(default=0, help='type -1 if you want to indicate one usage of contract service by confirming sale order for this product. Leave zero otherwise')


class AccountAnalyticAccountSlots(models.Model):
    _inherit = 'account.analytic.account'

    available_slots = fields.Integer(compute='_compute_available_slots', readonly=True, help='remaining number of slots left per contract')

    @api.one
    def _compute_available_slots(self):
        lines = self.env['sale.order.line'].search(['&', '&', ('order_id.project_id', '=', self.id),
                                                    ('order_id.state', 'in', ['manual', 'done']),
                                                    '|',
                                                    ('price_unit', '=', '0'),
                                                    ('product_id.slots', '!=', '0')])
        self.available_slots = sum(lines.mapped(lambda r: r.product_id.slots))


class SaleOrderSlots(models.Model):
    _inherit = 'sale.order'

    available_slots = fields.Integer(related='project_id.available_slots', readonly=True, help='remaining number of slots left per contract')
