# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_ohada_reports = fields.Boolean("Financial Reports")

#E    totals_below_sections = fields.Boolean(related='company_id.totals_below_sections', string='Add totals below sections', readonly=False,
#E                                           help='When ticked, totals and subtotals appear below the sections of the report.')
