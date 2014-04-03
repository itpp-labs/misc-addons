# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from pytils import numeral

class res_partner(osv.Model):
    _inherit = "res.partner"
    def _get_default_bank_id(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for row in self.browse(cr, uid, ids, context):
            res[row.id] = self.bank_ids && self.bank_ids[0]
        return res

    _columns = {
        'represented_by':fields.char('Represented by', size=256, help='String for contracts'),
        'default_bank_id':fields.function(_get_default_bank_id, type='many2one')
        }

def _get_amount_in_words(self, cr, uid, ids, field_name, arg, context=None):
    res = {}

    for row in self.browse(cr, uid, ids, context):
        rubles = numeral.rubles(int(row.amount_total))
        copek_num = round(row.amount_total - int(row.amount_total))
        copek = numeral.choose_plural(int(copek_num), (u"копейка", u"копейки", u"копеек"))
        res[row.id] = ("%s %02d %s")%(rubles, copek_num, copek)

    return res

class sale_order(osv.Model):
    _inherit = 'sale.order'

    _columns = {
        'amount_total_in_words': fields.function(_get_amount_in_words, string='Amount in words', type='char'),

        }
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        invoice_vals = super(sale_order, self)._prepare_invoice(self, cr, uid, order, lines, context)
        invoice_vals['date_origin'] = order.date_order

class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def _get_partner_bank_id(self, cr, uid, context=None):
        company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=context)
        if not company_id:
            return None
        return company_id.partner_id.default_bank_id

    _columns = {
        'amount_total_in_words': fields.function(_get_amount_in_words, string='Amount in words', type='char'),
        'date_origin': fields.date('Origin date', required=False, readonly=True),
        }
    _defaults = {
        'partner_bank_id': _get_partner_bank_id,
        }

#class account_invoice_line(osv.Model):
#    _inherit = 'account.invoice.line'
#    def _get_synonym(self, cr, uid, ids, field_name, arg, context):
#        res = {}
#        for row in self.browse(cr, uid, ids, context):
#            res[row.id] = {}
#            res[row.id]['product_uom_qty'] = row.quantity
#            res[row.id]['product_uom'] = row.uos_id
#        return res
#
#    _columns = {
#        'product_uom_qty':fields.function(_get_synonym, multi='synonym', type='float'),
#        'product_uom':fields.function(_get_synonym, multi='synonym', type='many2one'),
#        }
