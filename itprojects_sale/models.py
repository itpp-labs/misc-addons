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
    def _get_project_alias(self, cursor, user, ids, field_name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = 'is%s@it-projects.info' % sale.id
        return res
    

    _columns = {
        'use_contract':fields.boolean('Contract', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'subscription':fields.boolean('Subscription', help='Subscription service'),
        'paid_total':fields.function(_paid_total, string='Paid total', type='float', multi='paid_total'),
        'paid_total_rate':fields.function(_paid_total, string='Paid rate', type='float', multi='paid_total'),
        'project_alias': fields.function(_get_project_alias, string='Support E-mail', type='char'),
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
            ('acceptance_act_signed', 'Acceptance Act Signed'),
            #('progress', 'Sales Order'),
            ('progress', 'Invoiced'),
            ('manual', 'Sale to Invoice'), # not used?
            ('shipping_except', 'Shipping Exception'),#sale_stock
            ('invoice_except', 'Invoice Exception'),
            #('done', 'Done'),
            ('done', 'Paid'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True)
        }
    _defaults = {
        'use_contract': False,
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
    def action_acceptance_act_signed(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids):
            vals = {'state':'acceptance_act_signed'}
            if not o.date_acceptance:
                vals.update({'date_acceptance':fields.date.context_today(self, cr, uid, context=context)})
                self.write(cr, uid, [o.id], vals)
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

    def action_contract_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'itprojects_sale', 'email_template_edi_sale_contract')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': False
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

