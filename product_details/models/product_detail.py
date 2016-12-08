# -*- coding: utf-8 -*-
from odoo import fields, models


def _get_detail_source(self):
    return []


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    detail_source = fields.Reference(
        selection=_get_detail_source, string='Details',
        help="You can choose a source where to store product details")


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    detail_source = fields.Reference(
        selection=_get_detail_source, string='Details',
        help="You can choose a source where to store lot/serial number details")
