# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID, fields, http
from openerp.http import request

from openerp.tools.translate import _

class website_sale_special_offer(http.Controller):
    @http.route(["/special-offer/<int:id>"], type='http', auth="public", website=True)
    def special_offer(self, id, **post):
        special_offer_obj = request.registry.get('website_sale_special_offer.special_offer')
        special_offer = special_offer_obj.browse(request.cr, SUPERUSER_ID, id)
        return self._render_special_offer(special_offer, **post)

    def _render_special_offer(self, special_offer, **post):
        # copy-paste from addons/website_sale/controllers/main.py::cart
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        order = request.website.sale_get_order(force_create=True)
        if not order:
            # repeat
            print 'force to create order'
            order = request.website.sale_get_order(force_create=True)
        if order:
            from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)
        else:
            compute_currency = lambda price: price

        values = {
            'order': order,
            'compute_currency': compute_currency,
            'suggested_products': [],
        }
        if order:
            _order = order
            if not context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        # new stuff
        values['special_offer'] = special_offer
        for line in special_offer.line_ids:
            order._cart_update(product_id=line.product_id.id, set_qty=line.product_uom_qty, update_existed=False, special_offer_line=line)

        return request.website.render("website_sale.cart", values)

    @http.route(["/website_sale_special_offer/get_cart_lines"], type='json', auth="public", website=True)
    def cart_lines(self,  **post):
        order = request.website.sale_get_order()
        result = []
        for line in order.order_line:
            result.append({
                'id':line.id,
                'price_total':request.website._render("website_sale_special_offer.line_price_total", {'line':line, 'user_id':request.website.user_id})
            })
        return result
