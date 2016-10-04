# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.tools.translate import _


class SaleOrderLineMakeGroupedInvoice(osv.osv_memory):
    _name = "sale.order.line.make.grouped.invoice"

    def make_grouped_invoice(self, cr, uid, ids, context=None):
        sales_order_line_obj = self.pool.get('sale.order.line')
        order_obj = self.pool.get('sale.order')
        invoice = self.pool.get('account.invoice')

        invoices = {}
        inv_lines = []
        orders = []

        for line in sales_order_line_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            if (not line.invoiced) and (line.state not in ('draft', 'cancel')):
                inv_line_id = sales_order_line_obj.invoice_line_create(cr, uid, [line.id])
                for lid in inv_line_id:
                    inv_lines.append(lid)
                    orders.append(line.order_id.id)
                    invoices.setdefault(line.order_id.partner_invoice_id.id or line.order_id.partner_id.id, []).append((line.order_id, [lid]))

        partner_currency = {}
        for o in order_obj.browse(cr, uid, orders, context=context):
            currency_id = o.pricelist_id.currency_id.id
            if (o.partner_id.id in partner_currency) and (partner_currency[o.partner_id.id] <> currency_id):
                raise osv.except_osv(
                    _('Error!'),
                    _('You cannot group sales having different currencies for the same partner.'))

            partner_currency[o.partner_id.id] = currency_id

        for val in invoices.values():
            res = order_obj._make_invoice(cr, uid, val[0][0], reduce(lambda x, y: x + y, [l for o, l in val], []), context=context)
            invoice_ref = ''
            origin_ref = ''
            for o, l in val:
                invoice_ref += (o.client_order_ref or o.name) + '|'
                origin_ref += (o.origin or o.name) + '|'
                order_obj.write(cr, uid, [o.id], {'state': 'progress'})
                cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (o.id, res))
                order_obj.invalidate_cache(cr, uid, ['invoice_ids'], [o.id], context=context)
            #remove last '|' in invoice_ref
            if len(invoice_ref) >= 1:
                invoice_ref = invoice_ref[:-1]
            if len(origin_ref) >= 1:
                origin_ref = origin_ref[:-1]
            invoice.write(cr, uid, [res], {'origin': origin_ref, 'name': invoice_ref})
