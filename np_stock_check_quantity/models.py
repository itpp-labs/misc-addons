# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _

class stock_move(osv.Model):
    _inherit = "stock.move"

    def onchange_quantity(self, cr, uid, ids, product_id, product_qty, product_uom, product_uos, context=None):
        res = super(stock_move, self).onchange_quantity(cr, uid, ids, product_id, product_qty, product_uom, product_uos)

        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, product_id)
        if product.qty_available < product_qty:
            res['warning'] = {
                'title':_('Quantity check'),
                'message':_('There are not enough quantity to move'),
            }
        return res
    def  _get_qty_shortage(self, cr, uid, ids, field_name, arg, context=None):
        print '_get_qty_shortage', ids
        product_obj = self.pool.get('product.product')
        moves = self.browse(cr, uid, ids, context=context)
        product_ids = []
        for move in moves:
            if move.product_id.id:
                product_ids.append(move.product_id.id)
        products = {}

        for p in self.pool.get('product.product').read(cr, uid, product_ids, ['qty_available'], context=context):
            print 'here', p
            products[p['id']]=p

        res = {}
        for move in moves:
            val = 0
            if move.product_id.id:
                val = move.product_qty - products[move.product_id.id]['qty_available']
                if val < 0:
                    val = 0
            res[move.id] = val
        return res
    _columns = {
        'qty_shortage':fields.function(_get_qty_shortage, type='float', string='Shortage')
    }
