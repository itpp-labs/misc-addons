from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
import werkzeug
import datetime
import time

from openerp.tools.translate import _

class calculator(http.Controller):
    @http.route(['/calculator/calc'], type='json', auth='public', website=True)
    def calc(self, **post):
        x_currency_in_id = int(post.get('x_currency_in_id'))
        x_currency_out_id = int(post.get('x_currency_out_id'))
        x_in_amount = int(post.get('x_in_amount'))

        currency_obj = request.registry.get('res.currency')

        print 'calculator', x_currency_in_id, x_currency_out_id, x_in_amount
        val = {'x_out_amount': currency_obj.compute(request.cr, SUPERUSER_ID, x_currency_in_id, x_currency_out_id, x_in_amount)}

        return val

    @http.route(['/calculator/currencies'], type='json', auth='public', website=True)
    def currencies(self, **post):
        print 'here'
        currency_obj = request.registry.get('res.currency')
        ids = currency_obj.search(request.cr, SUPERUSER_ID, [])

        val = ''
        for cur in currency_obj.browse(request.cr, SUPERUSER_ID, ids):
            val += '<option value="%s">%s</option>'% (cur.id, cur.name)
        return val
