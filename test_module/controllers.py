# -*- coding: utf-8 -*-
from openerp import http

# class TestModule(http.Controller):
#     @http.route('/test_module/test_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_module/test_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_module.listing', {
#             'root': '/test_module/test_module',
#             'objects': http.request.env['test_module.test_module'].search([]),
#         })

#     @http.route('/test_module/test_module/objects/<model("test_module.test_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_module.object', {
#             'object': obj
#         })