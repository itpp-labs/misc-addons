# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class fleet_odometer_oil(models.Model):
#     _name = 'fleet_odometer_oil.fleet_odometer_oil'

#     name = fields.Char()

class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    oil_km = fields.Float("oil_km")
