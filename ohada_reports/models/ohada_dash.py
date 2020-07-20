from odoo import api, fields, models
from odoo.addons.web.controllers.main import clean_action
import json
import logging
from datetime import datetime
from datetime import date

_logger = logging.getLogger(__name__)

DATA = {}

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
    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
    options = fields.Many2one("ohada.options")
    lines_value = fields.Text(compute='_get_dashes_info')
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a blocks of a Dashboard.")
    button_classes = fields.Text(compute='_get_button_classes')

    def action_data(self):
        report = self.env.ref('ohada_reports.ohada_report_dash')
        di_data = {}
        options_record = self.env.ref('ohada_reports.ohada_dashboard_options').sudo()
        dashboard_data = self.env.ref('ohada_reports.ohada_dashboard_data').sudo()
        year = options_record.current_year if self._context.get('change_options') else datetime.now().year
        all_entries = options_record.all_entries if self._context.get('change_options') else False
        options = {
            'all_entries':	all_entries,
            'analytic':	None,
            'cash_basis':	None,
            'comparison': {
                'date':	str(year - 1) + '-12-31',
                'filter':	'no_comparison',
                'number_period':	0,
                'periods':	[],
                'string':	'No comparison',
                },
            'date':	{
                'date_to': str(year) + '-12-31',
                'string': str(year),
                'filter': 'this_year',
                'date_from': str(year) + '-01-01'
                },
            'hierarchy':	None,
            'ir_filters':	None,
            'journals':	None,
            'partner':	None,
            'unfold_all':	False,
            'unfolded_lines':	[],
            'unposted_in_period':	False,
            }
        ctx = report._set_context(options)
        report = report.with_context(ctx)
        data = report._get_lines(options)
        report_diagram = self.env.ref('ohada_reports.ohada_report_dash_diagram')
        report_diagram = report_diagram.with_context(ctx)
        options['date'] = {'date_to': str(year-1) + '-12-31', 'string': str(year-1), 'filter': 'this_year',
                           'date_from': str(year-1) + '-01-01'}
        di_data['n-1'] = report_diagram._get_lines(options)
        options['date'] = {'date_to': str(year - 2) + '-12-31', 'string': str(year - 2), 'filter': 'this_year',
                           'date_from': str(year - 2) + '-01-01'}
        di_data['n-2'] = report_diagram._get_lines(options)
        options['date'] = {'date_to': str(year - 3) + '-12-31', 'string': str(year - 3), 'filter': 'this_year',
                           'date_from': str(year - 3) + '-01-01'}
        di_data['n-3'] = report_diagram._get_lines(options)
        fetched_data = {
            '_BZ': data[0]['columns'][0]['no_format_name'],
            '_BZ-1': di_data['n-1'][0]['columns'][0]['no_format_name'],
            '_XI': data[1]['columns'][0]['no_format_name'],
            '_XI-1': di_data['n-1'][1]['columns'][0]['no_format_name'],
            '_ZH': data[2]['columns'][0]['no_format_name'],
            '_ZH-1': di_data['n-1'][2]['columns'][0]['no_format_name'],
            'di_data': {
                '_BZ': [
                      [str(year-3), di_data['n-3'][0]['columns'][0]['no_format_name']],
                      [str(year-2), di_data['n-2'][0]['columns'][0]['no_format_name']],
                      [str(year-1), di_data['n-1'][0]['columns'][0]['no_format_name']],
                      [str(year), data[0]['columns'][0]['no_format_name']],
                    ],
                '_XI': [
                    [str(year - 3), di_data['n-3'][1]['columns'][0]['no_format_name']],
                    [str(year - 2), di_data['n-2'][1]['columns'][0]['no_format_name']],
                    [str(year - 1), di_data['n-1'][1]['columns'][0]['no_format_name']],
                    [str(year), data[1]['columns'][0]['no_format_name']],
                    ],
                '_ZH': [
                      {'count': di_data['n-3'][2]['columns'][0]['no_format_name'], 'l_month': str(year-1), 'l_month': str(year-2), 'l_month': str(year-3)},
                      {'count': di_data['n-2'][2]['columns'][0]['no_format_name'], 'l_month': str(year-1), 'l_month': str(year-2)},
                      {'count': di_data['n-1'][2]['columns'][0]['no_format_name'], 'l_month': str(year-1)},
                      {'count': data[2]['columns'][0]['no_format_name'], 'l_month': str(year)}
                    ],
              },
            '_XC': data[3]['columns'][0]['no_format_name'],
            '_XD': data[4]['columns'][0]['no_format_name'],
            'N37_RC': data[5]['columns'][0]['no_format_name'],
            'N37_IR': data[6]['columns'][0]['no_format_name'],
        }
        # global DATA
        # DATA = fetched_data
        dashboard_data.data = json.dumps(fetched_data)
        # Returning "Dashboard new" kanban form action
        return self.env.ref('ohada_reports.ohada_action_dash').read()[0]

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
                    report_data.append({
                        'name': report.shortname,
                        'id': str(report.id),
                        'title': report.name
                    })
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
               dash.name == dash.company_id.name

    def _get_button_classes(self):
        for dash in self:
            if dash.name_to_display == 'company':
                data = {'signNpay_button': ''}
                if not dash.env['ohada.disclosure'].search([]).filtered(lambda x: int(x.fiscalyear_id) == dash.current_year).id:
                    data['signNpay_button'] = 'disabled'
                    dash.button_classes = json.dumps(data)

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
        if action:
            ctx.update({
                    'id': report.id,
                    'model': report._name,
                    'report_options': report.make_temp_options(self.current_year)
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
        DATA = json.loads(self.env.ref('ohada_reports.ohada_dashboard_data').sudo().data)
        data = []
        if self.report_type == 'BS':
            for line_data in DATA['di_data']['_BZ']:
                data.append({'label': line_data[0], 'value': line_data[1], 'type': 'past'})
        if self.report_type == 'PL':
            for line_data in DATA['di_data']['_XI']:
                data.append({'label': line_data[0], 'value': line_data[1], 'type': 'past'})
        if self.report_type == 'CF':
            for line_data in DATA['di_data']['_ZH']:
                # data.append({'label': line_data['l_month'], 'value': float(line_data['count']), 'type': 'past'})
                data.append({'label': line_data['l_month'], 'value': 10.0, 'type': 'past'})
        return data

    def _get_dashes_info(self):
        DATA = json.loads(self.env.ref('ohada_reports.ohada_dashboard_data').sudo().data)
        for dash in self:
            year = dash.current_year
            if dash.name_to_display == 'company':
                date_to = year and str(year) + '-12-31' or False
                period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]

                data = {
                    'block_2': [],
                    'period_lock_status': "Opened",
                    'unposted_in_period': "With Draft Entries" if bool(dash.env['account.move'].search_count(period_domain)) else "All Entries Posted"
                }

                data['block_2'].append({'name': 'Added value', 'value': DATA['_XC']})
                data['block_2'].append({'name': 'EBITDA', 'value': DATA['_XD']})
                data['block_2'].append({'name': 'Accounting net income', 'value': DATA['N37_RC']})
                data['block_2'].append({'name': 'Income tax', 'value': DATA['N37_IR']})

                dash.lines_value = json.dumps(data)
            if dash.displayed_report_line:
                variation = 'n/a'
                current_year_value = DATA[dash.displayed_report_line.code]
                prev_year_value = DATA[dash.displayed_report_line.code + '-1']
                if prev_year_value != 0.0:
                    variation = '{:,.0f}%'.format(((current_year_value/prev_year_value)-1)*100)
                dash.lines_value = json.dumps({'this_year': str(year),
                                                'this_year_value': DATA[dash.displayed_report_line.code],
                                                'prev_year': str(year - 1),
                                                'prev_year_value': DATA[dash.displayed_report_line.code + '-1'],
                                                'variation': variation})

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

    def open_page(self, context):
        if context['page'] == 'company':
            return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'res.company',
                'res_id': self.company_id.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
        if context['page'] == 'Format':
            action = self.env.ref('base.action_res_company_form')
            action['view_id'] = self.env.ref('ohada_reports.ohada_view_company_form').id
            action['res_id'] = self.company_id.id
            action['context'] = self.env.context
            action['target'] = 'current'
            return action.read()[0]
        if context['page'] == 'Disclosure form view':
            id = self.env['ohada.disclosure'].search([]).filtered(lambda x: int(x.fiscalyear_id) == self.current_year).id
            if not id:
                return None
            return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ohada.disclosure',
                'res_id': id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
        if context['page'] == 'Data import':
            id = self.env['ir.ui.menu'].search([]).filtered(lambda x: x.display_name == 'Accounting').id
            return {
                'type': 'ir.actions.act_url',
                'name': 'contract',
                'url': '/web#model=account.move&action=import&mode=import_balance&menu_id=%s' %(id),
                'target': 'self'
            }

    def run_update_note_relevance(self):
        note_relevance = self.env['note.relevance']
        note_relevance.update_note_relevance()

    def preview_pdf(self):
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


class OhadaDashData(models.Model):
    _name = "ohada.dash.data"

    data = fields.Text()
