# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID

class sale_order(osv.Model):
    _inherit = "sale.order"

    def _paid_total(self, cursor, user, ids, field_name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            paid = 0.0
            for invoice in sale.invoice_ids:
                if invoice.state in ('paid'):
                    paid += invoice.amount_total
            if paid:
                res[sale.id] = {
                    'paid_total':paid,
                    'paid_total_rate': min(100.0, paid * 100.0 / (sale.amount_total or 1.00)),
                    }
            else:
                res[sale.id] = {
                    'paid_total':0.0,
                    'paid_total_rate':0.0,
                    }
        return res

    _columns = {
        'use_contract':fields.boolean('Contract', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'paid_total':fields.function(_paid_total, string='Paid total', type='float', multi='paid_total'),
        'paid_total_rate':fields.function(_paid_total, string='Paid rate', type='float', multi='paid_total'),
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('contract_draft', 'Contract Draft'),
            ('contract_sent', 'Contract Sent'),
            ('contract_scan_received', 'Contract Scan Received'),
            ('contract_paused', 'Contract Paused'),
            ('contract_signed', 'Contract Signed'),
            ('prepayment', 'Waiting Prepayment'), # not use_contract
            ('development', 'Development'),
            ('review', 'Review'),
            ('acceptance_act_sent', 'Acceptance Act Sent'),
            ('acceptance_act_signed', 'Acceptance Act Sent'),
            #('progress', 'Sales Order'),
            ('progress', 'Invoiced'), # not used?
            ('manual', 'Sale to Invoice'), # not used?
            ('shipping_except', 'Shipping Exception'),#sale_stock
            ('invoice_except', 'Invoice Exception'),
            #('done', 'Done'),
            ('done', 'Paid'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True)
        }
    _defaults = {
        'use_contract': True,
        }

    def action_wait2(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if not o.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
            #noprod = self.test_no_product(cr, uid, o, context)
            #if (o.order_policy == 'manual') or noprod:
            #    self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            #else:
            #    self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            if o.use_contract:
                self.write(cr, uid, [o.id], {'state': 'contract_draft'})
            else:
                #TODO avans
                pass
            self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
        return True

    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        new_order_lines = []
        for line in order_lines:
            if line.product_id.type != 'service':
                new_order_lines.append(line)
        return super(sale_order, self)._create_pickings_and_procurements(cr, uid, order, new_order_lines, picking_id, context)
    #def action_register_prepayment(self, cr, uid, ids, context=None):

    #def invoice_ids_get(self, cr, uid, ids, *args):
    #    res = []
    #    for order in self.browse(cr, uid, ids, context={}):
    #        res += order.invoice_ids
    #    return res

