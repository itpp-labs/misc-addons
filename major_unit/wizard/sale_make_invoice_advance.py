# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

JOURNAL_DOMAIN=[('trade_in', '=', True)]

class SaleAdvancePaymentInvInherit(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(
        selection_add=[('trade_in', 'Trade-in payment (creates trade-in invoice only)'),
                       ('complete_trade_in', 'Complete Payment (creates trade-in invoice and an invoice with deducted amount)')])
    trade_in_amount = fields.Float('Trade-in Amount', compute='_compute_trade_in_amount')
    # linked_invoice_ids = fields.Many2many('account.invoice')
    journal_id = fields. Many2one('account.journal', string='Trade-in Journal', domain=JOURNAL_DOMAIN,
                                  default=lambda self: self.env['account.journal'].search(JOURNAL_DOMAIN) or False)
    linked_invoice_line_ids = fields.One2many('sale.advance.payment.inv.line', 'parent_id', string="Linked Invoices")

    @api.depends('advance_payment_method')
    @api.onchange('advance_payment_method')
    def _compute_trade_in_amount(self):
        sale_obj = self.env['sale.order']
        order = sale_obj.browse(self._context.get('active_ids'))[0]
        for record in self:
            if record.advance_payment_method in ['complete_trade_in', 'trade_in']:
                record.trade_in_amount = sum([ti.trade_equity for ti in order.trade_in_mu_ids] + [0])

    @api.onchange('advance_payment_method')
    def _onchange_advance_payment_method(self):
        if self.advance_payment_method in ['complete_trade_in', 'trade_in']:
            sale_obj = self.env['sale.order']
            order = sale_obj.browse(self._context.get('active_ids'))[0]
            invoice_ids = self.env['account.invoice'].search([('origin', '=', order.name)])
            # self.linked_invoice_ids = [(6, False, invoice_ids.ids)]

            self.linked_invoice_line_ids = [
                                               # remove old lines
                                               (5, None, None)
                                           ] + [
                (0, None, {
                    'invoice_id': i.id,
                })
                for i in invoice_ids
            ]

    def _create_trade_in_invoice(self, order):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']

        account_id = False
        if self.product_id.id:
            account_id = order.fiscal_position_id.map_account(
                self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id).id
        if not account_id:
            inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _(
                    'There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (self.product_id.name,))

        taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes).ids
        else:
            tax_ids = taxes.ids

        so_lines = []
        for ti in order.trade_in_mu_ids:
            so_line = self.env['sale.order.line'].create({
                'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                'price_unit': ti.trade_equity,
                'product_uom_qty': 0.0,
                'order_id': order.id,
                'discount': 0.0,
                'product_uom': ti.product_id.uom_id.id,
                'product_id': ti.product_id.id,
                'tax_id': [(6, 0, tax_ids)],
                'is_downpayment': True,
                'is_trade_in_payment': True,
            })
            so_lines.append(so_line)

        invoice = inv_obj.create({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': _('Trade-in Payment'),
                'origin': order.name,
                'account_id': account_id,
                'price_unit': sol.price_unit,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': sol.product_id.uom_id.id,
                'product_id': sol.product_id.id,
                'sale_line_ids': [(6, 0, [sol.id])],
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
                'account_analytic_id': order.analytic_account_id.id or False,
            }) for sol in so_lines],
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
            'user_id': order.user_id.id,
            'comment': order.note,
            'is_trade_in_payment': True,
        })
        invoice.compute_taxes()
        invoice.message_post_with_view('mail.message_origin_link',
                                       values={'self': invoice, 'origin': order},
                                       subtype_id=self.env.ref('mail.mt_note').id)
        return invoice

    @api.multi
    def create_invoices(self):

        if self.advance_payment_method not in ['complete_trade_in', 'trade_in']:
            return super(SaleAdvancePaymentInvInherit, self).create_invoices()

        # TODO: there should be the only order. CHECK IT
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        invoice_env = self.env['account.invoice']
        ti_invoice = False
        if self.advance_payment_method == 'trade_in' or not any(sale_orders.order_line.filtered(lambda ol: ol.is_trade_in_payment)):
            ti_invoice = self._create_trade_in_invoice(sale_orders)

        if self.advance_payment_method == 'complete_trade_in':
            # super method creates the invoice and returns the action
            sale_orders.action_invoice_create(final=True)
            invoices = invoice_env.search([('origin', '=', sale_orders.name)])
            invoices.action_invoice_open()
            ti_invoice = ti_invoice or invoices.filtered(lambda i: i.is_trade_in_payment)
            ti_invoice.pay_and_reconcile(self.journal_id)

        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}


class SaleAdvancePaymentInvLine(models.TransientModel):
    _name = "sale.advance.payment.inv.line"

    parent_id = fields.Many2one('sale.advance.payment.inv', readonly=True)

    invoice_id = fields.Many2one('account.invoice')
    is_trade_in_payment = fields.Boolean('Trade-in Invoice', default=True, states={'paid': [('readonly', True)]})
    vendor_id = fields.Many2one('res.partner', related='invoice_id.partner_id')
    date_invoice = fields.Date(string='Invoice Date', related="invoice_id.date_invoice")
    date_due = fields.Date(string='Due Date', related="invoice_id.date_due")
    origin = fields.Char(string='Source Document', related="invoice_id.origin")
    amount_total_signed = fields.Monetary(string='Total in Invoice Currency', related="invoice_id.amount_total_signed")
    residual_signed = fields.Monetary(string='Amount Due in Invoice Currency', related="invoice_id.residual_signed")
    state = fields.Selection(string='Status', related="invoice_id.state")
    # technical field
    currency_id = fields.Many2one('res.currency', string='Currency', related="invoice_id.currency_id")
