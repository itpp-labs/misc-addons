# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class WebWebsiteConfigSettings(models.TransientModel):

    _inherit = "base.config.settings"

    group_multi_website = fields.Boolean(
        string="Multi Website for Backend",
        help="Show Website Switcher in backend",
        implied_group="web_website.group_multi_website",
    )
