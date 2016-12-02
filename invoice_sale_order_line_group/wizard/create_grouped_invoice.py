# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.tools.translate import _
from openerp import models, fields, api


class GroupedInvoiceWizard(osv.osv_memory):
    _name = "sale_line.grouped_invoice_wizard"

    # TODO: don't use old api
    def make_grouped_invoice(self, cr, uid, ids, context=None):
        sales_order_line_obj = self.pool.get('sale.order.line')
        order_obj = self.pool.get('sale.order')
        invoice = self.pool.get('account.invoice')

        invoices = {}
        inv_lines = []
        orders = []
        created_ids = []

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
            if (o.partner_id.id in partner_currency) and (partner_currency[o.partner_id.id] != currency_id):
                raise osv.except_osv(
                    _('Error!'),
                    _('You cannot group sales having different currencies for the same partner.'))

            partner_currency[o.partner_id.id] = currency_id

        for val in invoices.values():
            res = order_obj._make_invoice(cr, uid, val[0][0], reduce(lambda x, y: x + y, [l for o, l in val], []), context=context)
            invoice_ref = ''
            origin_ref = ''
            for o in set([o for o, l in val]):
                invoice_ref += (o.client_order_ref or o.name) + '|'
                origin_ref += (o.origin or o.name) + '|'
                order_obj.write(cr, uid, [o.id], {'state': 'progress'})
                cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (o.id, res))
            order_obj.invalidate_cache(cr, uid, ['invoice_ids'], [o.id], context=context)
            # remove last '|' in invoice_ref
            if len(invoice_ref) >= 1:
                invoice_ref = invoice_ref[:-1]
            if len(origin_ref) >= 1:
                origin_ref = origin_ref[:-1]
            invoice.write(cr, uid, [res], {'origin': origin_ref, 'name': invoice_ref})
            created_ids.append(res)

        if context.get('open_invoices', False):
            return self.open_invoices(cr, uid, ids, created_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def open_invoices(self, cr, uid, ids, invoice_ids, context=None):
        """ open a view on one of the given invoice_ids """
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
        tree_id = tree_res and tree_res[1] or False

        result = {
            'name': _('Invoice'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'view_id': False,
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'context': {'type': 'out_invoice'},
            'type': 'ir.actions.act_window',
        }

        if len(invoice_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % invoice_ids
        elif len(invoice_ids) == 1:
            result['views'] = [(form_id, 'form')]
            result['res_id'] = invoice_ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result


class GroupedInvoiceWizard2(models.TransientModel):
    _inherit = "sale_line.grouped_invoice_wizard"

    invoiced_line_ids = fields.Many2many('sale.order.line', readonly=True)
    draft_line_ids = fields.Many2many('sale.order.line', readonly=True)
    invoiced_count = fields.Integer(readonly=True)
    draft_count = fields.Integer(readonly=True)

    @api.model
    def default_get(self, fields_list):
        result = super(GroupedInvoiceWizard2, self).default_get(fields_list)
        line_obj = self.env['sale.order.line']
        invoiced_lines = line_obj.browse(self._context.get('active_ids', [])).filtered("invoiced")
        draft_lines = line_obj.browse(self._context.get('active_ids', [])).filtered(lambda r: r.order_id.state in ['draft', 'cancel'])
        result['invoiced_line_ids'] = [(6, 0, invoiced_lines.ids)]
        result['draft_line_ids'] = [(6, 0, draft_lines.ids)]
        result['invoiced_count'] = len(invoiced_lines)
        result['draft_count'] = len(draft_lines)
        return result
