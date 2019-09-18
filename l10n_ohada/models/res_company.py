# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

#E    totals_below_sections = fields.Boolean(
#E        string='Add totals below sections',
#E        help='When ticked, totals and subtotals appear below the sections of the report.')