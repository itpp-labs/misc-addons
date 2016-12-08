# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _selection_details(self):
        return []

    details = fields.Reference(
        selection='_selection_details', string='Details',
        help="You can choose a source where to store product details")


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def _selection_details(self):
        return []

    details = fields.Reference(
        selection='_selection_details', string='Details',
        help="You can choose a source where to store lot/serial number details")
