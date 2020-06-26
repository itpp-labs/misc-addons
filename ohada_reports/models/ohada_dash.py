from odoo import api, fields, models
from odoo.addons.web.controllers.main import clean_action
import json
import logging
from datetime import datetime
from datetime import date

_logger = logging.getLogger(__name__)


class OhadaDash(models.Model):
    _name = "ohada.dash"
    _description = "OHADA dashboard"
    _order = "sequence"

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
    current_year = fields.Integer(related='options.current_year', string="Current Year")
    currency_id = fields.Char(related='company_id.currency_id.symbol', string='Currency symbol')
    reports = fields.Text(compute='_compute_reports')
    bundle_reports = fields.Text(compute='_compute_bundle_reports')
    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
    options = fields.Many2one("ohada.options")
    lines_value = fields.Text(compute='_get_BS_PL_CD_dashes')
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a blocks of a Dashboard.")

    def _compute_reports(self):
        for dash in self:
            reports_list = []
            # TODO: type field maybe needs for another reasons
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

    def _compute_bundle_reports(self):
        for dash in self:
            data = []
            for report in self.env['ohada.financial.html.report'].search([('type', '=', 'main')]):
                data.append({'name': report.name, 'id': report.id})
            dash.bundle_reports = json.dumps(data)

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

    def open_wizard(self):
        return self.env.ref('ohada_reports.change_options_wizard').sudo().read()[0]

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
        report_cf = self.env['ohada.financial.html.report'].search([('code', '=', report.code)], limit=1)
        options = report_cf._get_options()
        year = self.current_year
        options.update({
            'date': {'date_to': str(year) + '-12-31', 'string': str(year), 'filter': 'this_year', 'date_from': str(year) + '-01-01'},
            'all_entries': self.options.sudo().all_entries,
        })
        if action:
            ctx.update({
                    'id': report.id,
                    'model': report._name,
                    'report_options': options
                    # 'report_options': report.make_temp_options(self.current_year)
            })
        action['context'] = ctx
        return {
            'name': action['name'],
            'type': action['type'],
            'tag': action['tag'],
            'res_model': 'ohada.financial.html.report',
            'help': action['help'],
            'context': ctx,
        }

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
        data = []
        fetched_data = self.fetch_di_data(self.current_year, self.options.sudo().all_entries)
        if self.report_type == 'BS':
            for line_data in fetched_data['di_data']['BS']:
                data.append({'label': line_data[0], 'value': line_data[1], 'type': 'past'})
        if self.report_type == 'PL':
            for line_data in fetched_data['di_data']['PL']:
                data.append({'label': line_data[0], 'value': line_data[1], 'type': 'past'})
        if self.report_type == 'CF':
            for line_data in fetched_data['di_data']['CF']:
                data.append({'label': line_data['l_month'], 'value': line_data['count'], 'type': 'past'})
        # Code below needs for dash loading acceleration
        # data.append({'label': '2020', 'value': 10, 'type': 'past'})
        # data.append({'label': '2019', 'value': 2, 'type': 'past'})
        # data.append({'label': '2018', 'value': 8, 'type': 'past'})
        # data.append({'label': '2017', 'value': 20, 'type': 'past'})
        return data

    def _get_BS_PL_CD_dashes(self):
        report = self.env['ohada.financial.html.report']
        options = report.make_temp_options()
        ctx = report._set_context(options)
        for dash in self:
            year = dash.current_year
            if dash.name == 'YourCompany':
                date_to = year and str(year) + '-12-31' or False
                period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]

                data = {
                    'block_2': [],
                    'period_lock_status': "Opened",
                    'unposted_in_period': "With Draft Entries" if bool(dash.env['account.move'].search_count(period_domain)) else "All Entries Posted"
                }

                xc_id = dash.env.ref('ohada_reports.account_financial_report_ohada_profitlost_XC').id
                xd_id = dash.env.ref('ohada_reports.account_financial_report_ohada_profitlost_XD').id
                rc_id = dash.env.ref('ohada_reports.ohada_financial_report_note37_RC').id
                ir_id = dash.env.ref('ohada_reports.ohada_financial_report_note37_IR').id

                current_company_id = dash.company_id
                d_date_to = year and date(year, 12, 31) or False
                if current_company_id.period_lock_date:
                    period_lock_date = date(current_company_id.period_lock_date.year, current_company_id.period_lock_date.month, current_company_id.period_lock_date.day)
                    if d_date_to and period_lock_date  >= d_date_to:
                        data['period_lock_status'] = "Closed for non-accountants"
                if current_company_id.fiscalyear_lock_date:
                    fiscalyear_lock_date = date(current_company_id.fiscalyear_lock_date.year, current_company_id.fiscalyear_lock_date.month, current_company_id.fiscalyear_lock_date.day)
                    if d_date_to and fiscalyear_lock_date  >= d_date_to:
                        data['period_lock_status'] = "All Closed"

                data['block_2'].append({'name': 'Added value', 'value': report.with_context(ctx)._get_lines(options, xc_id)[0]['columns'][0]['no_format_name']})
                data['block_2'].append({'name': 'EBITDA', 'value': report.with_context(ctx)._get_lines(options, xd_id)[0]['columns'][0]['no_format_name']})
                data['block_2'].append({'name': 'Accounting net income', 'value': report.with_context(ctx)._get_lines(options, rc_id)[0]['columns'][0]['no_format_name']})
                data['block_2'].append({'name': 'Income tax', 'value': report.with_context(ctx)._get_lines(options, ir_id)[0]['columns'][0]['no_format_name']})

                # Code below needs for dash loading acceleration
                # data = {
                #     'block_2': [],
                #     'period_lock_status': "Opened",
                #     'unposted_in_period': "All Entries Posted"
                # }
                # data['block_2'].append({'name': 'Added value', 'value': 0})
                # data['block_2'].append({'name': 'EBITDA', 'value': 0})
                # data['block_2'].append({'name': 'Accounting net income', 'value': 0})
                # data['block_2'].append({'name': 'Income tax', 'value': 0})
                dash.lines_value = json.dumps(data)
            if dash.displayed_report_line:
                value = report.with_context(ctx)._get_lines({
                    'ir_filters': None,
                    'date': {'date_to': str(year) + '-12-31',
                            'string': str(year),
                            'filter': 'this_year',
                            'date_from': str(year) + '-01-01'}
                }, dash.displayed_report_line.id)[0]['columns'][0]['name']
                value_prev = report.with_context(ctx)._get_lines({
                    'ir_filters': None,
                    'date': {'date_to': str(year - 1) + '-12-31',
                            'string': str(year - 1),
                            'filter': 'this_year',
                            'date_from': str(year - 1) + '-01-01'}
                }, dash.displayed_report_line.id)[0]['columns'][0]['name']
                dash.lines_value = json.dumps({'this_year': str(year), 'this_year_value': value[0],
                                            'prev_year': str(year - 1), 'prev_year_value': value_prev[0]})

    def fetch_di_data(self, year, all_entries):
        report = self.env['ohada.financial.html.report']
        data = dict()
        report_cf = self.env['ohada.financial.html.report'].search([('code', '=', 'CF')], limit=1)
        options = report_cf._get_options()
        options.update({
            'date': {'date_to': str(year) + '-12-31', 'string': str(year), 'filter': 'this_year', 'date_from': str(year) + '-01-01'},
            'all_entries': all_entries,
        })
        ctx = report._set_context(options)
        report = report.with_context(ctx)
        bz_id = self.env.ref('ohada_reports.account_financial_report_balancesheet_BZ').id
        xi_id = self.env.ref('ohada_reports.account_financial_report_ohada_profitlost_XI').id
        zh_id = self.env.ref('ohada_reports.account_financial_report_ohada_cashflow_ZH').id

        data['bz_d'] = report._get_lines(options, bz_id)[0]['columns'][0]['no_format_name']
        data['xi_d'] = report._get_lines(options, xi_id)[0]['columns'][0]['no_format_name']
        data['xi-1_d'] = report._get_lines({
                                            'ir_filters': None,
                                            'date': {'date_to': str(year - 1) + '-12-31',
                                                    'string': str(year - 1), 'filter': 'this_year',
                                                    'date_from': str(year - 1) + '-01-01'}
                                            }, xi_id)[0]['columns'][0]['no_format_name']
        data['zh_d'] = report._get_lines(options, zh_id)[0]['columns'][0]['no_format_name']
        data['zh-1_d'] = report._get_lines({
                                            'ir_filters': None,
                                            'date': {'date_to': str(year - 1) + '-12-31',
                                                    'string': str(year - 1), 'filter': 'this_year',
                                                    'date_from': str(year - 1) + '-01-01'}
                                            }, zh_id)[0]['columns'][0]['no_format_name']
        data['di_data'] = {'BS': [], 'PL': [], 'CF': []}
        data['di_data']['BS'] = [[str(year - 3), report._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 3) + '-12-31',
                                                        'string': str(year - 3),
                                                        'filter': 'this_year',
                                                        'date_from': str(year - 3) + '-01-01'}
                                                }, bz_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 2), report._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 2) + '-12-31',
                                                        'string': str(year - 2),
                                                        'filter': 'this_year',
                                                        'date_from': str(year - 2) + '-01-01'}
                                                }, bz_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 1), report._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 1) + '-12-31',
                                                        'string': str(year - 1),
                                                        'filter': 'this_year',
                                                        'date_from': str(year - 1) + '-01-01'}
                                                }, bz_id)[0]['columns'][0]['no_format_name']],
                                 [str(year), data['bz_d']]]

        data['di_data']['PL'] = [[str(year - 3), report._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 3) + '-12-31',
                                                         'string': str(year - 3),
                                                         'filter': 'this_year',
                                                         'date_from': str(year - 3) + '-01-01'}
                                                }, xi_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 2), report._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 2) + '-12-31',
                                                         'string': str(year - 2),
                                                         'filter': 'this_year',
                                                         'date_from': str(year - 2) + '-01-01'}
                                                }, xi_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 1), data['xi-1_d']],
                                 [str(year), data['xi_d']]]

        data['di_data']['CF'] = [{'l_month': str(year - 3), 'count': report._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 3) + '-12-31',
                                                         'string': str(year - 3),
                                                         'filter': 'this_year',
                                                         'date_from': str(year - 3) + '-01-01'}
                                                }, zh_id)[0]['columns'][0]['no_format_name']},
                                 {'l_month': str(year - 2), 'count': report._get_lines({
                                                'ir_filters': None,
                                                'date': {'date_to': str(year - 2) + '-12-31',
                                                         'string': str(year - 2),
                                                         'filter': 'this_year',
                                                         'date_from': str(year - 2) + '-01-01'}
                                                }, zh_id)[0]['columns'][0]['no_format_name']},
                                 {'l_month': str(year - 1), 'count': data['zh-1_d']},
                                 {'l_month': str(year), 'count': data['zh_d']}]
        return data

    def company_page(self):
        action =  self.env.ref('base.action_res_company_form').read()[0]
        # action['context'] = {'id': self.company_id.id, 'name': self.company_id.name}
        
        import wdb;wdb.set_trace()
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.company",
            "views": [(action['id'], "form")],
            "view_ids": action['id'],
            "res_id": self.company_id.id,
            "target": "new"
        }

    def run_update_note_relevance(self):
        note_relevance = self.env['note.relevance']
        note_relevance.update_note_relevance()

    def preview_pdf(self):
        import wdb;wdb.set_trace()
        bundle = self.env['ohada.dash.print.bundle']
        if self.report_id.code == 'BS':
            return bundle.create({
                'balance_assets': True,
                'balance_liabilitities': True
            }).print_pdf()
        if self.report_id.code == 'PL':
            return bundle.create({
                'profit_loss': True
            }).print_pdf()
        if self.report_id.code == 'CF':
            return bundle.create({
                'cashflow': True
            }).print_pdf()

    def download_xlsx(self):
        bundle = self.env['ohada.dash.print.bundle']
        if self.report_id.code == 'BS':
            return bundle.create({
                'balance_assets': True,
                'balance_liabilitities': True
            }).print_xlsx()
        if self.report_id.code == 'PL':
            return bundle.create({
                'profit_loss': True
            }).print_xlsx()
        if self.report_id.code == 'CF':
            return bundle.create({
                'cashflow': True
            }).print_xlsx()


class ReportOhadaFinancialReport(models.Model):
    _inherit = "ohada.financial.html.report"

    dashboard_report_id = fields.One2many('ohada.dash', 'report_id')


class OhadaFinancialReportLine(models.Model):
    _inherit = "ohada.financial.html.report.line"

    dashboard_displayed_report_line = fields.One2many('ohada.dash', 'displayed_report_line')

class OhadaOptions(models.Model):
    _name = "ohada.options"

    current_year = fields.Integer(string="Current Year", default=str(datetime.now().year))
    dashboard = fields.One2many('ohada.dash', 'options')
    all_entries = fields.Boolean(string="Status of journal entries")
