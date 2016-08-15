# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class delivery_carrier(models.Model):
    _inherit = "delivery.carrier"

    _order = 'sequence,id'

    sequence = fields.Integer('Sequence', default=0)
