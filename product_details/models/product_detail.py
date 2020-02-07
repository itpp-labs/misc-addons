# Copyright 2016-2017 Stanislav Krotov <https://www.it-projects.info/team/ufaks>
# Copyright 2016-2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "base_details"]
