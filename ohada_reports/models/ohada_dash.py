# Copyright 2020 Vildan Safin <https://www.it-projects.info/team/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class OhadaDash(models.Model):
    _name = "ohada.dash"
    _description = "OHADA dashboard"

    name = fields.Char(required=True)
    name_to_display = fields.Selection([('name', 'Name'),
                                        ('company', 'Company')],
                                        default='name')
    display_name = fields.Char(compute='_compute_display_name')
    active = fields.Boolean()
    show_on_dashboard = fields.Boolean()
    sequence = fields.Integer()
    color = fields.Integer('Color index')
    type = fields.Selection([('report', 'Report'),
                             ('info_button', 'Info button'),
                             ('note_button', 'Note button'),
                             ('other_button', 'Other button'),
                             ('mix', 'Mix')],
                            required=True)
    # required if type == ‘report’.
    report_id = fields.Many2one('ohada.financial.html.report', string='OHADA report')
    # required only if type == ‘report’.
    displayed_report_line = fields.Many2one('ohada.financial.html.report.line')
    chart_type = fields.Selection([('barChart', 'Bar chart'),
                                   ('lineChart', 'Line chart')])
    dash_size = fields.Selection([('small', 'Small'),
                                  ('middle', 'Middle'),
                                  ('large', 'Large')])

    def _compute_display_name(self):
        self.display_name = self.name_to_display


class ReportOhadaFinancialReport(models.Model):
    _inherit = "ohada.financial.html.report"

    dashboard_report_id = fields.One2many('ohada.dash', 'report_id')


class OhadaFinancialReportLine(models.Model):
    _inherit = "ohada.financial.html.report.line"

    dashboard_displayed_report_line = fields.One2many('ohada.dash', 'displayed_report_line')
