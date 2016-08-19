# -*- coding: utf-8 -*-

from openerp import fields
from openerp import models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    oil_change_odometer = fields.Float("Last oil change (odometer)")
