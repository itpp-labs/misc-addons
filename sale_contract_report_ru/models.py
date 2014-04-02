# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from pytils import numeral

class res_partner(osv.Model):
    _inherit = "res.partner"
    _columns = {
        'represented_by':fields.char('Represented by', size=256, help='String for contracts'),
        }

class sale_order(osv.Model):
    _inherit = 'sale.order'

    def _get_amount_in_words(self, cr, uid, ids, field_name, arg, context):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            rubles = numeral.rubles(int(row.amount_total))
            copek_num = round(row.amount_total - int(row.amount_total))
            copek = numeral.choose_plural(int(copek_num), (u"копейка", u"копейки", u"копеек"))
            res[row.id] = ("%s %02d %s")%(rubles, copek_num, copek)

        return res


    _columns = {
        'amount_total_in_words': fields.function(_get_amount_in_words, string='Amount in words', type='char'),

        }
