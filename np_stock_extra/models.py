# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _

class stock_move(osv.Model):
    _inherit = "stock.move"

    def onchange_quantity(self, cr, uid, ids, product_id, product_qty, product_uom, product_uos, location_id=None, context=None):
        res = super(stock_move, self).onchange_quantity(cr, uid, ids, product_id, product_qty, product_uom, product_uos)

        if not product_id:
            return res

        if not location_id:
            return res

        qty_available = self._get_qty_available(cr, uid, product_id, location_id, context=context)
        if qty_available < product_qty:
            res['warning'] = {
                'title':_('Quantity check'),
                'message':_('There are not enough quantity to move'),
            }
        return res
    def _get_qty_available(self, cr, uid, product_id, location_id, context=None):
        print '_get_qty_available', product_id, location_id, context
        product_obj = self.pool.get('product.product')
        context = context or {}
        c = context.copy()
        c.update({ 'states': ('done',), 'what': ('in', 'out') , 'location':location_id, 'compute_child':False})
        return product_obj.get_product_available(cr, uid, [product_id], context=c)[product_id]

    def _get_qty_shortage(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for move in self.read(cr, uid, ids, ['product_id', 'product_qty', 'location_id'], context=context):
            val = 0
            print 'move', move
            if move['product_id'] and move['location_id']:
                val = move['product_qty'] - self._get_qty_available(cr, uid, move['product_id'][0], move['location_id'][0], context=context)
                if val < 0:
                    val = 0
            res[move['id']] = val
        return res
    _columns = {
        'qty_shortage':fields.function(_get_qty_shortage, type='float', string='Shortage')
    }
