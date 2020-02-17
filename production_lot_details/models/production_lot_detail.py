# Copyright 2017 Stanislav Krotov <https://www.it-projects.info/team/ufaks>
# Copyright 2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import models


class ProductionLot(models.Model):
    _name = "stock.production.lot"
    _inherit = ["stock.production.lot", "base_details"]
