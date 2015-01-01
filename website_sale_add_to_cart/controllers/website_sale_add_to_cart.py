# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug

class pos_website_sale(http.Controller):
    @http.route(['/shop/get_order_numbers'], type='json', auth="public", website=True)
    def get_order_numbers(self):
        res = {}
        order = request.website.sale_get_order()
        if order:
            for line in order.website_order_line:
                res[line.product_id.id] = line.product_uom_qty
        return res
