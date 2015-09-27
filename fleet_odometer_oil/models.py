# -*- coding: utf-8 -*-

from openerp import models, fields, api


class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    oil_change_odometer = fields.Float("Last oil change (odometer)")
