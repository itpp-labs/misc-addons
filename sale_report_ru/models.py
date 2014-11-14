# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from pytils import numeral

class res_partner(osv.Model):
    _inherit = "res.partner"
    def _get_default_bank_id(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for row in self.browse(cr, uid, ids, context):
            res[row.id] = row.bank_ids and row.bank_ids[0].id or None
        return res

    _columns = {
        'represented_by':fields.char('Represented by', size=256, help='String for contracts'),
        'default_bank_id':fields.function(_get_default_bank_id, type='many2one', obj='res.partner.bank')
        }

CURRENCY_RU = {
    'USD': (u"доллар", u"доллара", u"долларов"),
    'KZT': (u"тенге", u"тенге", u"тенге"),
    'RUB': (u"рубль", u"рубля", u"рублей"),
}

CURRENCY_CENTS_RU = {
    'USD': (u"цент", u"цента", u"центов"),
    'RUB': (u"копейка", u"копейки", u"копеек"),
}
def money_to_words(amount, code):
    rubles_num_in_words = numeral.in_words(amount)
    rubles = numeral.choose_plural(amount, CURRENCY_RU[code])
    copek_num = round(amount - amount)
    copek = numeral.choose_plural(int(copek_num), CURRENCY_CENTS_RU[code]) if code in CURRENCY_CENTS_RU else ''
    if copek:
        return ("%s %s %02d %s")%(rubles_num_in_words, rubles, copek_num, copek)
    else:
        return ("%s %s")%(rubles_num_in_words, rubles)

def _get_amount_in_words(self, cr, uid, ids, field_name, arg, context=None):
    res = {}

    for row in self.browse(cr, uid, ids, context):
        code = row.currency_id.name
        if code not in CURRENCY_RU:
            code = 'RUB'
        res[row.id] = money_to_words(row.amount_total, code)

    return res

class sale_order(osv.Model):
    _inherit = 'sale.order'

    _columns = {
        'date_acceptance': fields.date('Acceptance act date', required=False, readonly=False),
        'amount_total_in_words': fields.function(_get_amount_in_words, string='Amount in words', type='char'),

        }
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        invoice_vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context)
        invoice_vals['date_origin'] = order.date_order
        return invoice_vals

class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def _get_partner_bank_id(self, cr, uid, context=None):
        company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=context)
        company_obj = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        if not company_obj:
            return None
        return company_obj.partner_id.default_bank_id.id

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
