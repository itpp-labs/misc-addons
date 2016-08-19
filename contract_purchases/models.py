# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp


class AccountAnalyticAccount(osv.Model):
    _inherit = "account.analytic.account"

    def _negative(self, res):
        for k in res:
            res[k] *= -1
        return res

    def _supplier_fix_price_to_invoice_calc(self, cr, uid, ids, name, arg, context=None):
        purc_obj = self.pool.get('purchase.order')
        res = dict(((id, 0.0) for id in ids))
        for account in self.browse(cr, uid, ids, context=context):
            purchase_ids = purc_obj.search(cr, uid, [('contract_id', '=', account.id), ('invoiced', '=', False)], context=context)
            for purchase in purc_obj.browse(cr, uid, purchase_ids, context=context):
                res[account.id] += purchase.amount_untaxed
                for invoice in purchase.invoice_ids:
                    if invoice.state != 'cancel':
                        res[account.id] -= invoice.amount_untaxed
        return self._negative(res)

    def _supplier_remaining_ca_calc(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for account in self.browse(cr, uid, ids, context=context):
            res[account.id] = min(account.supplier_amount_max - account.supplier_ca_invoiced, account.supplier_fix_price_to_invoice)
        return res

    def _ca_invoiced_calc_inherit(self, cr, uid, ids, name, arg, context=None):
        res = {}
        res_final = {}
        child_ids = tuple(ids)  # We don't want consolidation for each of these fields because those complex computation is resource-greedy.
        for i in child_ids:
            res[i] = 0.0
        if not child_ids:
            return res

        if child_ids:
            # Search all invoice lines not in cancelled state that refer to this analytic account
            inv_line_obj = self.pool.get("account.invoice.line")
            inv_lines = inv_line_obj.search(cr, uid, [('account_analytic_id', 'in', child_ids), ('invoice_id.state', '!=', 'cancel'), ('invoice_id.journal_id.type', '=', 'sale')], context=context)
            for line in inv_line_obj.browse(cr, uid, inv_lines, context=context):
                res[line.account_analytic_id.id] += line.price_subtotal
        for acc in self.browse(cr, uid, res.keys(), context=context):
            res[acc.id] = res[acc.id] - (acc.timesheet_ca_invoiced or 0.0)

        res_final = res
        return res_final

    def _supplier_ca_invoiced_calc(self, cr, uid, ids, name, arg, context=None):
        res = {}
        res_final = {}
        child_ids = tuple(ids)  # We don't want consolidation for each of these fields because those complex computation is resource-greedy.
        for i in child_ids:
            res[i] = 0.0
        if not child_ids:
            return res

        if child_ids:
            # Search all invoice lines not in cancelled state that refer to this analytic account
            inv_line_obj = self.pool.get("account.invoice.line")
            inv_lines = inv_line_obj.search(cr, uid, [('account_analytic_id', 'in', child_ids), ('invoice_id.state', '!=', 'cancel'), ('invoice_id.journal_id.type', '=', 'purchase')], context=context)
            for line in inv_line_obj.browse(cr, uid, inv_lines, context=context):
                res[line.account_analytic_id.id] += line.price_subtotal
        # for acc in self.browse(cr, uid, res.keys(), context=context):
        #    res[acc.id] = res[acc.id] - (acc.timesheet_ca_invoiced or 0.0)

        res_final = res
        return self._negative(res_final)

    def _supplier_get_total_estimation(self, account):
        total = super(AccountAnalyticAccount, self)._get_total_estimation(account)

        if account.supplier_fix_price_invoices:
            total += account.supplier_amount_max

        return total

    def _get_total_invoiced(self, account):
        total = super(AccountAnalyticAccount, self)._get_total_invoiced(account)
        if account.supplier_fix_price_invoices:
            total += account.supplier_ca_invoiced

        return total

    def _get_total_remaining(self, account):
        total = super(AccountAnalyticAccount, self)._get_total_remaining(account)
        if account.supplier_fix_price_invoices:
            total += account.supplier_remaining_ca

        return total

    def _get_total_toinvoice(self, account):
        total = super(AccountAnalyticAccount, self)._get_total_toinvoice(account)
        if account.supplier_fix_price_invoices:
            total += account.supplier_fix_price_to_invoice
        return total

    def _get_supplier_ids(self, cr, uid, ids, field_names, args, context=None):
        purc_obj = self.pool.get('purchase.order')
        res = {}
        for account in self.browse(cr, uid, ids, context=context):
            res[account.id] = []
            purchase_ids = purc_obj.search(cr, uid, [('contract_id', '=', account.id)], context=context)
            for p in purc_obj.browse(cr, uid, purchase_ids, context=context):
                res[account.id].append(p.partner_id.id)
        return res

    _columns = {
        'supplier_fix_price_invoices': fields.boolean('Fixed Price (Supplier)'),

        'supplier_fix_price_to_invoice': fields.function(_supplier_fix_price_to_invoice_calc, type='float', string='Remaining Time',
                                                         help="Sum of quotations for this contract."),

        'supplier_remaining_ca': fields.function(_supplier_remaining_ca_calc, type='float', string='Remaining Revenue',
                                                 help="Computed using the formula: Max Invoice Price - Invoiced Amount.",
                                                 digits_compute=dp.get_precision('Account')),

        'supplier_ca_invoiced': fields.function(_supplier_ca_invoiced_calc, type='float', string='Invoiced Amount',
                                                help="Total customer invoiced amount for this account.",
                                                digits_compute=dp.get_precision('Account')),

        'supplier_amount_max': fields.float('Max. Invoice Price',
                                            help="Keep empty if this contract is not limited to a total fixed price."),
        'ca_invoiced': fields.function(_ca_invoiced_calc_inherit, type='float', string='Invoiced Amount',
                                       help="Total customer invoiced amount for this account.",
                                       digits_compute=dp.get_precision('Account')),
        'supplier_ids': fields.function(_get_supplier_ids, string='Suppliers', type='many2many', relation='res.partner')


    }

    def _check_supplier_amount_max(self, cr, uid, ids, context=None):
        return all([record.supplier_amount_max <= 0 for record in self.browse(cr, uid, ids, context)])

    _constraints = [
        (_check_supplier_amount_max, 'Expected value for supplier should be negative', ['supplier_amount_max']),
    ]


class PurchaseOrder(osv.Model):
    _inherit = "purchase.order"
    _columns = {
        'contract_id': fields.many2one('account.analytic.account', 'Analytic Account'),

    }


class PurchaseOrderLine(osv.Model):
    _inherit = 'purchase.order.line'

    def create(self, cr, uid, vals, context=None):
        if vals.get('order_id'):
            order = self.pool.get('purchase.order').browse(cr, uid, vals.get('order_id'))
            if order and order.contract_id and not vals.get('account_analytic_id'):
                vals['account_analytic_id'] = order.contract_id.id
        order = super(PurchaseOrderLine, self).create(cr, uid, vals, context=context)
        return order

    _defaults = {
        'date_planned': lambda self, cr, uid, context=None: fields.date.context_today(self, cr, uid, context=context)
    }
