# -*- coding: utf-8 -*-
from openerp import http

# class WebsiteSaleBirthdate(http.Controller):
#     @http.route('/website_sale_birthdate/website_sale_birthdate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_sale_birthdate/website_sale_birthdate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_sale_birthdate.listing', {
#             'root': '/website_sale_birthdate/website_sale_birthdate',
#             'objects': http.request.env['website_sale_birthdate.website_sale_birthdate'].search([]),
#         })

#     @http.route('/website_sale_birthdate/website_sale_birthdate/objects/<model("website_sale_birthdate.website_sale_birthdate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_sale_birthdate.object', {
#             'object': obj
#         })