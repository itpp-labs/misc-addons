# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _

from openerp.addons.website_sale.controllers.main import website_sale


class controller(website_sale):

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        res = super(controller, self).confirm_order(**post)

        order = request.website.sale_get_order(context=request.context)
        if not all([line.product_uom_qty <= line.product_id.virtual_available
                for line in order.order_line]):
            return request.redirect("/shop/cart")
        return res
