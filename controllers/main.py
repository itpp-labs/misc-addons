# -*- coding: utf-8 -*-
import logging

from openerp import http
from openerp.http import request

_logger = logging.getLogger(__name__)


class BarcodeController(http.Controller):

    @http.route(['/barcode/web/'], type='http', auth='user')
    def a(self, debug=False, **kw):
        if not request.session.uid:
            return http.local_redirect('/web/login?redirect=/barcode/web')

        return request.render('stock_picking_barcode.barcode_index')
