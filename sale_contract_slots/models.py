# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProductTemplateSlots(models.Model):
    _inherit = 'product.template'

    slots = fields.Integer(default=0, help="""Number of slots to sale in bulk.
    Can be negative to account slots usage (usually used for zero priced dummy products).
    Leave zero if you don't use slots.""")


class AccountAnalyticAccountSlots(models.Model):
    _inherit = 'account.analytic.account'

    available_slots = fields.Integer(compute='_compute_available_slots', readonly=True, help='remaining number of slots left in this contract', store=True)
    paid_slots = fields.Integer(compute='_compute_paid_slots', readonly=True, help='paid slots in this contract', store=True)

    order_ids = fields.One2many('sale.order', 'project_id')

    @api.depends('order_ids.state')
    @api.one
    def _compute_available_slots(self):
        lines = self.env['sale.order.line'].search(['&', ('order_id.project_id', '=', self.id),
                                                    '|', '&',
                                                    ('order_id.state', 'in', ['manual', 'done']),
                                                    ('price_unit', '=', '0'),
                                                    '&',
                                                    ('order_id.state', '=', 'done'),
                                                    ('product_id.slots', '>', '0')])

        self.available_slots = sum(lines.mapped(lambda r: r.product_id.slots * r.product_uom_qty))

    @api.depends('order_ids.state')
    @api.one
    def _compute_paid_slots(self):
        lines = self.env['sale.order.line'].search(['&', '&', ('order_id.project_id', '=', self.id),
                                                    ('order_id.state', '=', 'done'),
                                                    ('product_id.slots', '>', '0')])
        self.paid_slots = sum(lines.mapped(lambda r: r.product_id.slots))


class SaleOrderSlots(models.Model):
    _inherit = 'sale.order'

    available_slots = fields.Integer(related='project_id.available_slots', readonly=True, help='remaining number of slots left in this contract')
    paid_slots = fields.Integer(related='project_id.paid_slots', readonly=True, help='paid slots in this contract')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
