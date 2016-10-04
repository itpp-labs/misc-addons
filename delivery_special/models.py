# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.tools import safe_eval


class DeliveryGrid(osv.osv):
    _inherit = "delivery.grid"

    def get_price(self, cr, uid, id, order, dt, context=None):
        total = 0
        weight = 0
        volume = 0
        quantity = 0
        special_delivery = 0
        product_uom_obj = self.pool.get('product.uom')
        for line in order.order_line:
            if not line.product_id or line.is_delivery:
                continue
            q = product_uom_obj._compute_qty(cr, uid, line.product_uom.id, line.product_uom_qty, line.product_id.uom_id.id)
            weight += (line.product_id.weight or 0.0) * q
            volume += (line.product_id.volume or 0.0) * q
            special_delivery += (line.product_id.special_delivery or 0.0) * q
            quantity += q
        total = order.amount_total or 0.0

        return self.get_price_from_picking(cr, uid, id, total, weight, volume, quantity, special_delivery, context=context)

    def get_price_from_picking(self, cr, uid, id, total, weight, volume, quantity, special_delivery=0, context=None):
        grid = self.browse(cr, uid, id, context=context)
        price = 0.0
        ok = False
        price_dict = {'price': total, 'volume': volume, 'weight': weight, 'wv': volume * weight, 'quantity': quantity, 'special_delivery': special_delivery}
        for line in grid.line_ids:
            test = safe_eval(line.type + line.operator + str(line.max_value), price_dict)
            if test:
                if line.price_type == 'variable':
                    price = line.list_price * price_dict[line.variable_factor]
                else:
                    price = line.list_price
                ok = True
                break
        if not ok:
            raise osv.except_osv(_("Unable to fetch delivery method!"), _("Selected product in the delivery method doesn't fulfill any of the delivery grid(s) criteria."))

        return price


class DeliveryGridLine(osv.osv):
    _inherit = "delivery.grid.line"
    _columns = {
        'type': fields.selection([('weight', 'Weight'), ('volume', 'Volume'),
                                  ('wv', 'Weight * Volume'), ('price', 'Price'), ('quantity', 'Quantity'), ('special_delivery', 'Special Delivery')],
                                 'Variable', required=True),
    }


class ProductTemplate(osv.osv):
    _inherit = 'product.template'
    _columns = {
        'special_delivery': fields.integer('Special Delivery', help='Allows make special rules at delivery grid. Can be negative')
    }
    _defaults = {
        'special_delivery': 0,
    }
