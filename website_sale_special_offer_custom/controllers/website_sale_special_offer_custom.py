# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID, fields, http
from openerp.http import request

from openerp.tools.translate import _

from openerp.addons.website_sale_special_offer.controllers.website_sale_special_offer import website_sale_special_offer as controller

class website_sale_special_offer_custom(controller):
    @http.route(["/kits"], type='http', auth="public", website=True)
    def special_offer_custom(self, **post):
        special_offer_obj = request.registry.get('website_sale_special_offer.special_offer')
        ids = special_offer_obj.search(request.cr, SUPERUSER_ID, [('active', '=', True)])
        special_offer = special_offer_obj.browse(request.cr, SUPERUSER_ID, ids[0])
        return self._render_special_offer(special_offer, **post)
