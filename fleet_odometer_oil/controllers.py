# -*- coding: utf-8 -*-
from openerp import http

# class FleetOdometerOil(http.Controller):
#     @http.route('/fleet_odometer_oil/fleet_odometer_oil/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fleet_odometer_oil/fleet_odometer_oil/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fleet_odometer_oil.listing', {
#             'root': '/fleet_odometer_oil/fleet_odometer_oil',
#             'objects': http.request.env['fleet_odometer_oil.fleet_odometer_oil'].search([]),
#         })

#     @http.route('/fleet_odometer_oil/fleet_odometer_oil/objects/<model("fleet_odometer_oil.fleet_odometer_oil"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fleet_odometer_oil.object', {
#             'object': obj
#         })