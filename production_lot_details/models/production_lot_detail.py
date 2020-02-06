from odoo import models


class ProductionLot(models.Model):
    _name = "stock.production.lot"
    _inherit = ["stock.production.lot", "base_details"]
