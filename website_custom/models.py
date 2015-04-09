from openerp import api, models, fields, SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.tools.translate import _

class website_custom(http.Controller):
    @http.route(['/website_custom/ribbons'], type='json', auth="public", website=True)
    def ribbons(self, ids):
        cr = request.cr
        uid = SUPERUSER_ID
        res = request.registry['product.template'].search_read(cr, uid, domain=[('default_code', 'in', ids)], fields=['id', 'website_style_ids', 'default_code'])

        return res
