# Copyright 2020 Vildan Safin <https://www.it-projects.info/team/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons.web.controllers.main import clean_action
import json
import logging
from datetime import datetime

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
    report_type = fields.Char(string='Report type', related='report_id.code')
    # required only if type == ‘report’.
    displayed_report_line = fields.Many2one('ohada.financial.html.report.line')
    chart_type = fields.Selection([('barChart', 'Bar chart'),
                                   ('lineChart', 'Line chart')])
    dash_size = fields.Selection([('small', 'Small'),
                                  ('middle', 'Middle'),
                                  ('large', 'Large')])
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda s: s.env.user.company_id
    )
    currency_id = fields.Char(related='company_id.currency_id.symbol', string='Currency symbol')
    reports = fields.Text(compute='_compute_reports')
    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
    current_year = fields.Integer(string='Date Current Action',default=datetime.now().year)

    def _compute_reports(self):
        for dash in self:
            reports_list = []
            if dash.type == 'note_button':
                reports_list = self.env['ohada.financial.html.report'].search([('type', '=', 'note'), ('secondary', '=', False)])
            if dash.type == 'info_button':
                reports_list = self.env['ohada.financial.html.report'].search([('type', '=', 'sheet'), ('secondary', '=', False)])
            report_data = []
            cnt = 0
            for report in reports_list:
                cnt += 1
                if dash.type == 'info_button':
                    report_data.append({'name': "SHEET R" + str(cnt), 'id': str(report.id)})
                else:
                    report_data.append({'name': report.shortname, 'id': str(report.id)})
            dash.reports = json.dumps(report_data)

    def _compute_buttons_ids(self):
        for dash in self:
            if dash.type == 'note_button':
                for report in self.env['ohada.financial.html.report'].search([('type', '=', 'note'), ('secondary', '=', False)]):
                    dash.button_ids += report
                    report.dash_button_ids = dash

    def _compute_display_name(self):
        for dash in self:
            if dash.name_to_display == 'name':
                dash.display_name = dash.name
            else:
                dash.display_name = 'Company' + str(dash.id)

    @api.multi
    def open_action(self):
        report = self.env['ohada.financial.html.report'].search([('code', '=', self.report_type)])
        return self.return_action(report)

    @api.multi
    def open_action_by_id(self, params):
        report = self.env['ohada.financial.html.report'].browse(int(params['id']))
        try:
            return self.return_action(report)
        except:
            _logger.error("Exception occured in return_action at ohada.dash model, probably 'action' is absent")
            return 0

    @api.multi
    def return_action(self, report):
        action = self.env['ir.actions.client'].sudo().search([('name', '=', report.name)]).read()[0]
        action = clean_action(action)
        ctx = self.env.context.copy()
        if action:
            ctx.update({
                    'id': report.id,
                    'report_options': report.make_temp_options(),
                    'model': report._name
            })
        action['context'] = ctx
        return action

    @api.multi
    def _kanban_dashboard_graph(self):
        for dash in self:
            if dash.report_id.code == 'BS':
                dash.kanban_dashboard_graph = json.dumps([{'values': dash._get_graph_data(), 'title': "Balance sheet", 'key': 'BS'}])
            if dash.report_id.code == 'PL':
                dash.kanban_dashboard_graph = json.dumps([{'values': dash._get_graph_data(), 'title': "Profit and Loss", 'key': 'PL'}])
            if dash.report_id.code == 'CF':
                dash.kanban_dashboard_graph = json.dumps([{'values': dash._get_graph_data(), 'title': "Cashflow", 'key': 'CF'}])

    @api.multi
    def _get_graph_data(self):
        # report = self.report_id
        data = []
        fetched_data = self.fetch_di_data()
        if self.report_type == 'BS':
            for line_data in fetched_data['di_data']['BS']:
                data.append({'label': line_data[0], 'value': line_data[1], 'type': 'past'})
        if self.report_type == 'PL':
            for line_data in fetched_data['di_data']['PL']:
                data.append({'label': line_data[0], 'value': line_data[1], 'type': 'past'})
        if self.report_type == 'CF':
            for line_data in fetched_data['di_data']['CF']:
                data.append({'label': line_data['l_month'], 'value': line_data['count'], 'type': 'past'})
        return data
    
    def fetch_di_data(self):
        report = self.env['ohada.financial.html.report']
        data = dict()
        year = self.current_year
        report_cf = self.env['ohada.financial.html.report'].search([('code', '=', 'CF')], limit=1)
        options = report_cf._get_options()
        options.update({
            'date': {'date_to': str(year) + '-12-31', 'string': str(year), 'filter': 'this_year', 'date_from': str(year) + '-01-01'},
            'all_entries': False,
        })
        ctx = report._set_context(options)
        bz_id = self.env.ref('ohada_reports.account_financial_report_balancesheet_BZ').id
        xi_id = self.env.ref('ohada_reports.account_financial_report_ohada_profitlost_XI').id
        zh_id = self.env.ref('ohada_reports.account_financial_report_ohada_cashflow_ZH').id
        data['bz_d'] = report.with_context(ctx)._get_lines(options, bz_id)[0]['columns'][0]['no_format_name']
        data['xi_d'] = report.with_context(ctx)._get_lines(options, xi_id)[0]['columns'][0]['no_format_name']
        data['xi-1_d'] = report.with_context(ctx)._get_lines({
                                            'ir_filters': None,
                                            'date': {'date_to': str(year - 1) + '-12-31',
                                                    'string': str(year - 1), 'filter': 'this_year',
                                                    'date_from': str(year - 1) + '-01-01'}
                                            }, xi_id)[0]['columns'][0]['no_format_name']
        data['zh_d'] = report.with_context(ctx)._get_lines(options, zh_id)[0]['columns'][0]['no_format_name']
        data['zh-1_d'] = report.with_context(ctx)._get_lines({
                                            'ir_filters': None,
                                            'date': {'date_to': str(year - 1) + '-12-31',
                                                    'string': str(year - 1), 'filter': 'this_year',
                                                    'date_from': str(year - 1) + '-01-01'}
                                            }, zh_id)[0]['columns'][0]['no_format_name']
        data['di_data'] = {'BS': [], 'PL': [], 'CF': []}
        data['di_data']['BS'] = [[str(year - 3), report.with_context(ctx)._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 3) + '-12-31',
                                                        'string': str(year - 3),
                                                        'filter': 'this_year',
                                                        'date_from': str(year - 3) + '-01-01'}
                                                }, bz_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 2), report.with_context(ctx)._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 2) + '-12-31',
                                                        'string': str(year - 2),
                                                        'filter': 'this_year',
                                                        'date_from': str(year - 2) + '-01-01'}
                                                }, bz_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 1), report.with_context(ctx)._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 1) + '-12-31',
                                                        'string': str(year - 1),
                                                        'filter': 'this_year',
                                                        'date_from': str(year - 1) + '-01-01'}
                                                }, bz_id)[0]['columns'][0]['no_format_name']],
                                 [str(year), data['bz_d']]]

        data['di_data']['PL'] = [[str(year - 3), report.with_context(ctx)._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 3) + '-12-31',
                                                         'string': str(year - 3),
                                                         'filter': 'this_year',
                                                         'date_from': str(year - 3) + '-01-01'}
                                                }, xi_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 2), report.with_context(ctx)._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 2) + '-12-31',
                                                         'string': str(year - 2),
                                                         'filter': 'this_year',
                                                         'date_from': str(year - 2) + '-01-01'}
                                                }, xi_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 1), data['xi-1_d']],
                                 [str(year), data['xi_d']]]

        data['di_data']['CF'] = [{'l_month': str(year - 3), 'count': report.with_context(ctx)._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 3) + '-12-31',
                                                         'string': str(year - 3),
                                                         'filter': 'this_year',
                                                         'date_from': str(year - 3) + '-01-01'}
                                                }, zh_id)[0]['columns'][0]['no_format_name']},
                                 {'l_month': str(year - 2), 'count': report.with_context(ctx)._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 2) + '-12-31',
                                                         'string': str(year - 2),
                                                         'filter': 'this_year',
                                                         'date_from': str(year - 2) + '-01-01'}
                                                }, zh_id)[0]['columns'][0]['no_format_name']},
                                 {'l_month': str(year - 1), 'count': data['zh-1_d']},
                                 {'l_month': str(year), 'count': data['zh_d']}]
        return data

    @api.multi
    def change_current_year(self, year):
        self.current_year = year


class ReportOhadaFinancialReport(models.Model):
    _inherit = "ohada.financial.html.report"

    dashboard_report_id = fields.One2many('ohada.dash', 'report_id')


class OhadaFinancialReportLine(models.Model):
    _inherit = "ohada.financial.html.report.line"

    dashboard_displayed_report_line = fields.One2many('ohada.dash', 'displayed_report_line')
