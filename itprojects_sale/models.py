# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID

class sale_order(osv.Model):
    _inherit = "sale.order"

    _columns = {
        'use_contract':fields.boolean('Договор', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
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
        print 'action_wait', ids
        for o in self.browse(cr, uid, ids):
            if not o.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
            #noprod = self.test_no_product(cr, uid, o, context)
            #if (o.order_policy == 'manual') or noprod:
            #    self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            #else:
            #    self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            print 'use_contract', o.id, o.use_contract
            if o.use_contract:
                self.write(cr, uid, [o.id], {'state': 'contract_draft'})
            else:
                #TODO avans
                pass
            self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
        return True
