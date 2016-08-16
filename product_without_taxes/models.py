# -*- coding: utf-8 -*-
from openerp import models
from openerp.osv import fields as old_fields

import openerp.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_price_unit_without_taxes(self, cr, uid, ids, fname, arg, context=None):
        res = {}
        for r in self.browse(cr, uid, ids, context=context):
            line = r
            val = line.tax_id.compute_all(
                line.price_unit,
                1,
                line.product_id,
                line.order_id.partner_id)
            res[r.id] = val.get('total', 0.0)
        return res

    _columns = {
        'price_unit_without_taxes': old_fields.function(_get_price_unit_without_taxes, type='float', string='Unit Price (W/o taxes)', digits_compute=dp.get_precision('Product Price'))
    }


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _get_price_unit_without_taxes(self, cr, uid, ids, fname, arg, context=None):
        res = {}
        for r in self.browse(cr, uid, ids, context=context):
            line = r
            val = line.invoice_line_tax_id.compute_all(
                line.price_unit,
                1,
                line.product_id,
                line.invoice_id.partner_id)
            res[r.id] = val.get('total', 0.0)
        return res

    _columns = {
        'price_unit_without_taxes': old_fields.function(_get_price_unit_without_taxes, type='float', string='Unit Price (W/o taxes)', digits_compute=dp.get_precision('Product Price'))
    }
