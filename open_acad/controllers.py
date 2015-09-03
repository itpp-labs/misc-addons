# -*- coding: utf-8 -*-
from openerp import http

# class OpenAcad(http.Controller):
#     @http.route('/open_acad/open_acad/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/open_acad/open_acad/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('open_acad.listing', {
#             'root': '/open_acad/open_acad',
#             'objects': http.request.env['open_acad.open_acad'].search([]),
#         })

#     @http.route('/open_acad/open_acad/objects/<model("open_acad.open_acad"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('open_acad.object', {
#             'object': obj
#         })