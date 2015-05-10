# -*- coding: utf-8 -*-
from openerp import http

# class ResPartnerStripEmail(http.Controller):
#     @http.route('/res_partner_strip_email/res_partner_strip_email/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/res_partner_strip_email/res_partner_strip_email/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('res_partner_strip_email.listing', {
#             'root': '/res_partner_strip_email/res_partner_strip_email',
#             'objects': http.request.env['res_partner_strip_email.res_partner_strip_email'].search([]),
#         })

#     @http.route('/res_partner_strip_email/res_partner_strip_email/objects/<model("res_partner_strip_email.res_partner_strip_email"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('res_partner_strip_email.object', {
#             'object': obj
#         })