# Copyright 2016-2017 Stanislav Krotov <https://www.it-projects.info/team/ufaks>
# Copyright 2016-2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "base_details"]
