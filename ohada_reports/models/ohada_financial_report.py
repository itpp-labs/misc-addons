# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import copy
import ast
import datetime
import base64
import io

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, ustr
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.pycompat import izip
from odoo import http
from odoo.http import content_disposition, request
# import wdb

class ReportOhadaFinancialReport(models.Model):
    _name = "ohada.financial.html.report"
    _description = "OHADA Report (HTML)"
    _inherit = "ohada.report"

    name = fields.Char(translate=True)
    shortname = fields.Char(translate=True)
    code = fields.Char('Code')
    debit_credit = fields.Boolean('Show Credit and Debit Columns')
    line_ids = fields.One2many('ohada.financial.html.report.line', 'financial_report_id', string='Lines')
    date_range = fields.Boolean('Based on date ranges', default=True, help='specify if the report use date_range or single date')
    comparison = fields.Boolean('Allow comparison', default=True, help='display the comparison filter')
    cash_basis = fields.Boolean('Allow cash basis mode', help='display the option to switch to cash basis mode')
    analytic = fields.Boolean('Allow analytic filters', help='display the analytic filters')
    hierarchy_option = fields.Boolean('Enable the hierarchy option', help='Display the hierarchy choice in the report options')
    show_journal_filter = fields.Boolean('Allow filtering by journals', help='display the journal filter in the report')
    unfold_all_filter = fields.Boolean('Show unfold all filter', help='display the unfold all options in report')
    company_id = fields.Many2one('res.company', string='Company')
    generated_menu_id = fields.Many2one(
        string='Menu Item', comodel_name='ir.ui.menu', copy=False,
        help="The menu item generated for this report, or None if there isn't any."
    )
    parent_id = fields.Many2one('ir.ui.menu', related="generated_menu_id.parent_id", readonly=False)
    tax_report = fields.Boolean('Tax Report', help="Set to True to automatically filter out journal items that have the boolean field 'tax_exigible' set to False")
    applicable_filters_ids = fields.Many2many('ir.filters', domain="[('model_id', '=', 'account.move.line')]",
                                              help='Filters that can be used to filter and group lines in this report.')
    type = fields.Selection([('main', 'Main'),
                             ('note', 'Note'),
                             ('sheet', 'Sheet'),
                             ('cover', 'Cover'),
                             ('other', 'Other'),],
                            default=False)
    sequence = fields.Integer()
    header = fields.Char(default=False)
    double_report = fields.Boolean(default=False)
    secondary = fields.Boolean(default=False)
    description = fields.Text('Notes', track_visibility=False)
    description_pad = fields.Char('Description PAD', pad_content_field='description')
    default_columns_quantity = fields.Integer(default=False)


    _sql_constraints = [
        ('code_uniq', 'unique (code)', "A report with the same code already exists."),
    ]

    @api.one
    @api.constrains('code')
    def _code_constrains(self):
        if self.code and self.code.strip().lower() in __builtins__.keys():
            raise ValidationError('The code "%s" is invalid on report with name "%s"' % (self.code, self.name))

    @api.model
    def write_description(self, id, **kw):
        self = self.env.browse(id)
        self.description = kw['summary']
        return True

    @api.model
    def print_bundle_xlsx(self, options, response, reports_ids=None):
        reports_ids = reports_ids.split(',')
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        for report_id in reports_ids:
            if report_id != 'notes':
                self.env['ohada.financial.html.report'].browse(int(report_id)).get_xlsx(options, response, print_bundle=True, workbook=workbook)
            else:
                options['comparison']['filter'] = 'previous_period'
                for report in self.env['ohada.financial.html.report'].search([('type', '=', 'note'), ('secondary', '=', False)]):
                    report.get_xlsx(options, response, print_bundle=True, workbook=workbook)


        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response

    @api.model
    def print_bundle_pdf(self, options, reports_ids=None, minimal_layout=True):
        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # base_url = 'http://127.0.0.1:8069'
        reports_ids = reports_ids.split(',')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.user.company_id,
        }
        body = self.env['ir.ui.view'].render_template("ohada_reports.print_template", values=dict(rcontext),)
        body_html = b''
        for report_id in reports_ids:
            if report_id != 'notes':
                body_html += self.env['ohada.financial.html.report'].browse(int(report_id)).get_html(options)
            else:
                options['comparison']['filter'] = 'previous_period'
                for report in self.env['ohada.financial.html.report'].search([('type', '=', 'note'), ('secondary', '=', False)]):
                    body_html += report.get_html(options)

        body = body.replace(b'<body class="o_ohada_reports_body_print">',
                            b'<body class="o_ohada_reports_body_print">' + body_html)
        body = body.replace(b'<table style="margin-top:10px;margin-bottom:10px;color:#001E5A;font-weight:normal;"',
                            b'<table style="font-size:8px !important;margin-top:10px;margin-bottom:10px;color:#001E5A;font-weight:normal;"')

        if minimal_layout:
            header = ''
            footer = self.env['ir.actions.report'].render_template("ohada_reports.internal_layout_ohada",
                                                                   values=rcontext)
            spec_paperformat_args = {'data-report-margin-top': 10, 'data-report-header-spacing': 10}
            footer = self.env['ir.actions.report'].render_template("web.minimal_layout",
                                                                   values=dict(rcontext, subst=True, body=footer))
        else:
            rcontext.update({
                'css': '',
                'o': self.env.user,
                'res_company': self.env.user.company_id,
            })
            header = self.env['ir.actions.report'].render_template("web.external_layout", values=rcontext)
            header = header.decode('utf-8')  # Ensure that headers and footer are correctly encoded
            spec_paperformat_args = {}
            # Default header and footer in case the user customized web.external_layout and removed the header/footer
            headers = header.encode()
            footer = b''
            # parse header as new header contains header, body and footer
            try:
                root = lxml.html.fromstring(header)
                match_klass = "//div[contains(concat(' ', normalize-space(@class), ' '), ' {} ')]"

                for node in root.xpath(match_klass.format('header')):
                    headers = lxml.html.tostring(node)
                    headers = self.env['ir.actions.report'].render_template("web.minimal_layout",
                                                        values=dict(rcontext, subst=True, body=headers))

                for node in root.xpath(match_klass.format('footer')):
                    footer = lxml.html.tostring(node)
                    footer = self.env['ir.actions.report'].render_template("web.minimal_layout",
                                                            values=dict(rcontext, subst=True, body=footer))

            except lxml.etree.XMLSyntaxError:
                headers = header.encode()
                footer = b''
            header = headers

        landscape = False
        if len(self.with_context(print_mode=True).get_header(options)[-1]) > 5:
            landscape = True
        # wdb.set_trace()
        return self.env['ir.actions.report']._run_wkhtmltopdf(
            [body],
            header=header, footer=footer,
            landscape=landscape,
            specific_paperformat_args=spec_paperformat_args
        )

    def _get_column_name(self, field_content, field):
        comodel_name = self.env['account.move.line']._fields[field].comodel_name
        if not comodel_name:
            return field_content
        grouping_record = self.env[comodel_name].browse(field_content)
        return grouping_record.name_get()[0][1] if grouping_record and grouping_record.exists() else _('Undefined')

    def _get_columns_name_hierarchy(self, options):
        '''Calculates a hierarchy of column headers meant to be easily used in QWeb.

        This returns a list of lists. An example for 1 period and a
        filter that groups by company and partner:

        [
          [{'colspan': 2, 'name': 'As of 02/28/2018'}],
          [{'colspan': 2, 'name': 'YourCompany'}],
          [{'colspan': 1, 'name': 'ASUSTeK'}, {'colspan': 1, 'name': 'Agrolait'}],
        ]

        The algorithm used to generate this loops through each group
        id in options['groups'].get('ids') (group_ids). E.g. for
        group_ids:

        [(1, 8, 8),
         (1, 17, 9),
         (1, None, 9),
         (1, None, 13),
         (1, None, None)]

        These groups are always ordered. The algorithm loops through
        every first elements of each tuple, then every second element
        of each tuple etc. It generates a header element every time
        it:

        - notices a change compared to the last element (e.g. when processing 17
          it will create a dict for 8) or,
        - when a split in the row above happened

        '''
        # wdb.set_trace()
        if not options.get('groups', {}).get('ids'):
            return False

        periods = [{'string': self.format_date(options), 'class': 'number'}] + options['comparison']['periods']

        # generate specific groups for each period
        groups = []
        for period in periods:
            if len(periods) == 1 and self.debit_credit:
                for group in options['groups'].get('ids'):
                    groups.append(({'string': _('Debit'), 'class': 'number'},) + tuple(group))
                for group in options['groups'].get('ids'):
                    groups.append(({'string': _('Crebit'), 'class': 'number'},) + tuple(group))
            for group in options['groups'].get('ids'):
                groups.append((period,) + tuple(group))

        # add sentinel group that won't be rendered, this way we don't
        # need special code to handle the last group of every row
        groups.append(('sentinel',) * (len(options['groups'].get('fields', [])) + 1))

        column_hierarchy = []

        # row_splits ensures that we do not span over a split in the row above.
        # E.g. the following is *not* allowed (there should be 2 product sales):
        # | Agrolait | Camptocamp |
        # |  20000 Product Sales  |
        row_splits = []

        for field_index, field in enumerate(['period'] + options['groups'].get('fields')):
            current_colspan = 0
            current_group = False
            last_group = False

            # every report has an empty, unnamed header as the leftmost column
            current_hierarchy_line = [{'name': '', 'colspan': 1}]

            for group_index, group_ids in enumerate(groups):
                current_group = group_ids[field_index]
                if last_group is False:
                    last_group = current_group

                if last_group != current_group or group_index in row_splits:
                    current_hierarchy_line.append({
                        # field_index - 1 because ['period'] is not part of options['groups']['fields']
                        'name': last_group.get('string') if field == 'period' else self._get_column_name(last_group, options['groups']['fields'][field_index - 1]),
                        'colspan': current_colspan,
                        'class': 'number',
                    })
                    last_group = current_group
                    current_colspan = 0
                    row_splits.append(group_index)

                current_colspan += 1

            column_hierarchy.append(current_hierarchy_line)

        return column_hierarchy

    def _get_columns_name(self, options):
        # wdb.set_trace()
        columns = [{'name': ''}]
        if self.debit_credit and not options.get('comparison', {}).get('periods', False):
            columns += [{'name': _('Debit'), 'class': 'number'}, {'name': _('Credit'), 'class': 'number'}]
        columns += [{'name': self.format_date(options), 'class': 'number'}]
        if options.get('comparison') and options['comparison'].get('periods'):
            for period in options['comparison']['periods']:
                columns += [{'name': period.get('string'), 'class': 'number'}]
            if options['comparison'].get('number_period') == 1 and not options.get('groups'):
                columns += [{'name': '%', 'class': 'number'}]

        if options.get('groups', {}).get('ids'):
            columns_for_groups = []
            for column in columns[1:]:
                for ids in options['groups'].get('ids'):
                    group_column_name = ''
                    for index, id in enumerate(ids):
                        column_name = self._get_column_name(id, options['groups']['fields'][index])
                        group_column_name += ' ' + column_name
                    columns_for_groups.append({'name': column.get('name') + group_column_name, 'class': 'number'})
            columns = columns[:1] + columns_for_groups

        return columns

    def _get_filter_journals(self):
        if self == self.env.ref('ohada_reports.account_financial_report_ohada_cashflow'):
            return self.env['account.journal'].search([('company_id', 'in', self.env.user.company_ids.ids or [self.env.user.company_id.id]), ('type', 'in', ['bank', 'cash'])], order="company_id, name")
        return super(ReportOhadaFinancialReport, self)._get_filter_journals()

    def _build_options(self, previous_options=None):
        options = super(ReportOhadaFinancialReport, self)._build_options(previous_options=previous_options)

        if self.filter_ir_filters:
            options['ir_filters'] = []

            previously_selected_id = False
            if previous_options and previous_options.get('ir_filters'):
                previously_selected_id = [f for f in previous_options['ir_filters'] if f.get('selected')]
                if previously_selected_id:
                    previously_selected_id = previously_selected_id[0]['id']
                else:
                    previously_selected_id = False

            for ir_filter in self.filter_ir_filters:
                options['ir_filters'].append({
                    'id': ir_filter.id,
                    'name': ir_filter.name,
                    'domain': ir_filter.domain,
                    'context': ir_filter.context,
                    'selected': ir_filter.id == previously_selected_id,
                })

        return options

    @api.model
    def _get_options(self, previous_options=None):
        if self.date_range:
            self.filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}
            if self.comparison:
                self.filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
        else:
            self.filter_date = {'date': '', 'filter': 'today'}
            if self.comparison:
                self.filter_comparison = {'date': '', 'filter': 'no_comparison', 'number_period': 1}
        self.filter_cash_basis = False if self.cash_basis else None
        if self.unfold_all_filter:
            self.filter_unfold_all = False
        if self.show_journal_filter:
            self.filter_journals = True
        self.filter_all_entries = False
        self.filter_analytic = self.analytic or None
        if self.analytic:
            self.filter_analytic_accounts = [] if self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids else None
            self.filter_analytic_tags = [] if self.env.user.id in self.env.ref('analytic.group_analytic_tags').users.ids else None
            #don't display the analytic filtering options if no option would be shown
            if self.filter_analytic_accounts is None and self.filter_analytic_tags is None:
                self.filter_analytic = None
        self.filter_hierarchy = True if self.hierarchy_option else None
        self.filter_ir_filters = self.applicable_filters_ids or None

        rslt = super(ReportOhadaFinancialReport, self)._get_options(previous_options)

        # If manual values were stored in the context, we store them as options.
        # This is useful for report printing, were relying only on the context is
        # not enough, because of the use of a route to download the report (causing
        # a context loss, but keeping the options).
        if self.env.context.get('financial_report_line_values'):
            rslt['financial_report_line_values'] = self.env.context['financial_report_line_values']

        return rslt

    def _set_context(self, options):
        ctx = super(ReportOhadaFinancialReport, self)._set_context(options)
        # We first restore the context for from_context lines from the options
        if options.get('financial_report_line_values'):
            ctx.update({'financial_report_line_values': options['financial_report_line_values']})

        return ctx

    def _create_action_and_menu(self, parent_id):
        # create action and menu with corresponding external ids, in order to
        # remove those entries when deinstalling the corresponding module
        module = self._context.get('install_module', 'ohada_reports')
        IMD = self.env['ir.model.data']
        for report in self:
            if not report.generated_menu_id and report.secondary != True:
                action_vals = {
                    'name': report._get_report_name(),
                    'tag': 'ohada_report',
                    'context': {
                        'model': 'ohada.financial.html.report',
                        'id': report.id,
                    },
                }
                action_xmlid = "%s.%s" % (module, 'ohada_financial_html_report_action_' + str(report.id))
                data = dict(xml_id=action_xmlid, values=action_vals, noupdate=True)
                action = self.env['ir.actions.client'].sudo()._load_records([data])

                menu_vals = {
                    'name': report._get_report_name(),
                    'parent_id': parent_id or IMD.xmlid_to_res_id('account.menu_finance_reports'),
                    'action': 'ir.actions.client,%s' % (action.id,),
                }
                menu_xmlid = "%s.%s" % (module, 'ohada_financial_html_report_menu_' + str(report.id))
                data = dict(xml_id=menu_xmlid, values=menu_vals, noupdate=True)
                menu = self.env['ir.ui.menu'].sudo()._load_records([data])

                self.write({'generated_menu_id': menu.id})

    @api.model
    def create(self, vals):
        parent_id = vals.pop('parent_id', False)
        res = super(ReportOhadaFinancialReport, self).create(vals)
        res._create_action_and_menu(parent_id)
        return res

    @api.multi
    def write(self, vals):
        parent_id = vals.pop('parent_id', False)
        res = super(ReportOhadaFinancialReport, self).write(vals)
        if parent_id:
            # this keeps external ids "alive" when upgrading the module
            for report in self:
                report._create_action_and_menu(parent_id)
        return res

    @api.multi
    def unlink(self):
        for report in self:
            default_parent_id = self.env['ir.model.data'].xmlid_to_res_id('account.menu_finance_reports')
            menu = self.env['ir.ui.menu'].search([('parent_id', '=', default_parent_id), ('name', '=', report.name)])
            if menu:
                menu.action.unlink()
                menu.unlink()
        return super(ReportOhadaFinancialReport, self).unlink()

    def _get_currency_table(self):
        used_currency = self.env.user.company_id.currency_id.with_context(company_id=self.env.user.company_id.id)
        currency_table = {}
        for company in self.env['res.company'].search([]):
            if company.currency_id != used_currency:
                currency_table[company.currency_id.id] = used_currency.rate / company.currency_id.rate
        return currency_table

    def _get_groups(self, domain, group_by):
        '''This returns a list of lists of record ids. Every list represents a
           domain to be used in a column in the report. The ids in the list are
           in the same order as `group_by`. Only groups containing an
           account.move.line are returned.

           E.g. with group_by=['partner_id', 'journal_id']:
           # partner_id  journal_id
           [(7,2),
            (7,5),
            (8,8)]
        '''
        if any([field not in self.env['account.move.line'] for field in group_by]):
            raise ValueError(_('Groupby should be a field from account.move.line'))
        domain = [domain] if domain else [()]
        group_by = ', '.join(['"account_move_line".%s' % field for field in group_by])
        all_report_lines = self.env['ohada.financial.html.report.line'].search([('id', 'child_of', self.line_ids.ids)])
        all_domains = expression.OR([ast.literal_eval(dom) for dom in all_report_lines.mapped('domain') if dom])
        all_domains = expression.AND([all_domains] + domain)
        tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=all_domains)
        sql = 'SELECT %s FROM %s WHERE %s GROUP BY %s ORDER BY %s' % (group_by, tables, where_clause, group_by, group_by)
        self.env.cr.execute(sql, where_params)
        return self.env.cr.fetchall()

    def _get_filter_info(self, options):
        if not options['ir_filters']:
            return False, False

        selected_ir_filter = [f for f in options['ir_filters'] if f.get('selected')]
        if selected_ir_filter:
            selected_ir_filter = selected_ir_filter[0]
        else:
            return False, False

        domain = ast.literal_eval(selected_ir_filter['domain'])
        group_by = ast.literal_eval(selected_ir_filter['context']).get('group_by', [])
        return domain, group_by

    @api.multi
    def _get_lines(self, options, line_id=None):
        # wdb.set_trace()
        line_obj = self.line_ids
        if line_id:
            line_obj = self.env['ohada.financial.html.report.line'].search([('id', '=', line_id)])
        if options.get('comparison') and options.get('comparison').get('periods'):
            line_obj = line_obj.with_context(periods=options['comparison']['periods'])
        if options.get('ir_filters'):
            line_obj = line_obj.with_context(periods=options.get('ir_filters'))

        currency_table = self._get_currency_table()
        domain, group_by = self._get_filter_info(options)

        if group_by:
            options['groups'] = {}
            options['groups']['fields'] = group_by
            options['groups']['ids'] = self._get_groups(domain, group_by)

        amount_of_periods = len((options.get('comparison') or {}).get('periods') or []) + 1
        amount_of_group_ids = len(options.get('groups', {}).get('ids') or []) or 1
        linesDicts = [[{} for _ in range(0, amount_of_group_ids)] for _ in range(0, amount_of_periods)]

        res = line_obj.with_context(
            cash_basis=options.get('cash_basis'),
            filter_domain=domain,
        )._get_lines(self, currency_table, options, linesDicts)
        return res

    def _get_report_name(self):
        return self.name

    @api.multi
    def _get_copied_name(self):
        '''Return a copied name of the ohada.financial.html.report record by adding the suffix (copy) at the end
        until the name is unique.

        :return: an unique name for the copied ohada.financial.html.report
        '''
        self.ensure_one()
        name = self.name + ' ' + _('(copy)')
        while self.search_count([('name', '=', name)]) > 0:
            name += ' ' + _('(copy)')
        return name

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        '''Copy the whole financial report hierarchy by duplicating each line recursively.

        :param default: Default values.
        :return: The copied ohada.financial.html.report record.
        '''
        self.ensure_one()
        if default is None:
            default = {}
        default.update({'name': self._get_copied_name()})
        copied_report_id = super(ReportOhadaFinancialReport, self).copy(default=default)
        for line in self.line_ids:
            line._copy_hierarchy(report_id=self, copied_report_id=copied_report_id)
        return copied_report_id


class OhadaFinancialReportLine(models.Model):
    _name = "ohada.financial.html.report.line"
    _description = "OHADA Report (HTML Line)"
    _order = "sequence"
    _parent_store = True

    name = fields.Char('Section Name', translate=True)
    code = fields.Char('Code')
    financial_report_id = fields.Many2one('ohada.financial.html.report', 'Financial Report')
    parent_id = fields.Many2one('ohada.financial.html.report.line', string='Parent', ondelete='cascade')
    children_ids = fields.One2many('ohada.financial.html.report.line', 'parent_id', string='Children')
    parent_path = fields.Char(index=True)
    sequence = fields.Integer()

    domain = fields.Char(default=None)
    formulas = fields.Char()
    groupby = fields.Char("Group by", default=False)
    figure_type = fields.Selection([('float', 'Float'), ('percents', 'Percents'), ('no_unit', 'No Unit')],
                                   'Type', default='float', required=True)
    print_on_new_page = fields.Boolean('Print On New Page', help='When checked this line and everything after it will be printed on a new page.')
    green_on_positive = fields.Boolean('Is growth good when positive', default=True)
    level = fields.Integer(required=True)
    special_date_changer = fields.Selection([
        ('from_beginning', 'From the beginning'),
        ('to_beginning_of_period', 'At the beginning of the period'),
        ('normal', 'Use given dates'),
        ('strict_range', 'Force given dates for all accounts and account types'),
        ('from_fiscalyear', 'From the beginning of the fiscal year'),
    ], default='normal')
    show_domain = fields.Selection([('always', 'Always'), ('never', 'Never'), ('foldable', 'Foldable')], default='foldable')
    hide_if_zero = fields.Boolean(default=False)
    action_id = fields.Many2one('ir.actions.actions')
    #E
    reference = fields.Char(string="Référence")
    flag = fields.Char(string="Flag", size=10)
    note_report_ids = fields.Many2many(comodel_name='ohada.financial.html.report', relation='financial_report_report_note', column1='financial_report', column2='report_note', string='Note Reports')
    note = fields.Char(string="Note", help="Note displayed in reports", default='none')
    displayed_sign = fields.Char(string="Displayed Sign", size=3)
    hidden_line = fields.Boolean(default=False)
    symbol = fields.Char(string="Symbol", default='none')
    header = fields.Boolean(default=False)
    header_columns = fields.Char(default=False)
    letter = fields.Char(string="letter", default=None)
    note_id = fields.Char(string="note action id", default='none')
    table_spacer = fields.Boolean(default=False)
    colspan = fields.Integer(default=1)
    rowspan = fields.Integer(default=1)
    columns_id = fields.One2many('ohada.custom.columns', 'line_id', default=False)


    _sql_constraints = [
        ('code_uniq', 'unique (code)', "A report line with the same code already exists."),
    ]

    @api.one
    @api.constrains('code')
    def _code_constrains(self):
        if self.code and self.code.strip().lower() in __builtins__.keys():
            raise ValidationError('The code "%s" is invalid on report line with name "%s"' % (self.code, self.name))

    @api.multi
    def _get_note_displayed(self): 
        for line in self:
            if len(line.note_report_ids) == 1:
                line.note = line.note_report_ids[0].code[1:]
            elif len(line.note_report_ids) > 1:
                for note in line.note_report_ids:
                    line.note = note.code[1:]
            else:
                line.note = ''
                
    @api.multi
    def _get_copied_code(self):
        '''Look for an unique copied code.

        :return: an unique code for the copied ohada.financial.html.report.line
        '''
        self.ensure_one()
        code = self.code + '_COPY'
        while self.search_count([('code', '=', code)]) > 0:
            code += '_COPY'
        return code

    @api.multi
    def _copy_hierarchy(self, report_id=None, copied_report_id=None, parent_id=None, code_mapping=None):
        ''' Copy the whole hierarchy from this line by copying each line children recursively and adapting the
        formulas with the new copied codes.

        :param report_id: The financial report that triggered the duplicate.
        :param copied_report_id: The copy of old_report_id.
        :param parent_id: The parent line in the hierarchy (a copy of the original parent line).
        :param code_mapping: A dictionary keeping track of mapping old_code -> new_code
        '''
        self.ensure_one()
        if code_mapping is None:
            code_mapping = {}
        # If the line points to the old report, replace with the new one.
        # Otherwise, cut the link to another financial report.
        if report_id and copied_report_id and self.financial_report_id.id == report_id.id:
            financial_report_id = copied_report_id.id
        else:
            financial_report_id = None
        copy_line_id = self.copy({
            'financial_report_id': financial_report_id,
            'parent_id': parent_id and parent_id.id,
            'code': self.code and self._get_copied_code(),
        })
        # Keep track of old_code -> new_code in a mutable dict
        if self.code:
            code_mapping[self.code] = copy_line_id.code
        # Copy children
        for line in self.children_ids:
            line._copy_hierarchy(parent_id=copy_line_id, code_mapping=code_mapping)
        # Update formulas
        if self.formulas:
            copied_formulas = self.formulas
            for k, v in code_mapping.items():
                for field in ['debit', 'credit', 'balance', 'amount_residual']:
                    suffix = '.' + field
                    copied_formulas = copied_formulas.replace(k + suffix, v + suffix)
            copy_line_id.formulas = copied_formulas

    def _query_get_select_sum(self, currency_table):
        """ Little function to help building the SELECT statement when computing the report lines.

            @param currency_table: dictionary containing the foreign currencies (key) and their factor (value)
                compared to the current user's company currency
            @returns: the string and parameters to use for the SELECT
        """
        extra_params = []
        select = '''
            COALESCE(SUM(\"account_move_line\".balance), 0) AS balance,
            COALESCE(SUM(\"account_move_line\".amount_residual), 0) AS amount_residual,
            COALESCE(SUM(\"account_move_line\".debit), 0) AS debit,
            COALESCE(SUM(\"account_move_line\".credit), 0) AS credit
        '''
        if currency_table:
            select = 'COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".balance * %s '
            select += 'ELSE \"account_move_line\".balance END), 0) AS balance, COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".amount_residual * %s '
            select += 'ELSE \"account_move_line\".amount_residual END), 0) AS amount_residual, COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".debit * %s '
            select += 'ELSE \"account_move_line\".debit END), 0) AS debit, COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".credit * %s '
            select += 'ELSE \"account_move_line\".credit END), 0) AS credit'

        if self.env.context.get('cash_basis'):
            for field in ['debit', 'credit', 'balance']:
                #replace the columns selected but not the final column name (... AS <field>)
                number_of_occurence = len(select.split(field)) - 1
                select = select.replace(field, field + '_cash_basis', number_of_occurence - 1)
        return select, extra_params

    def _get_with_statement(self, financial_report):
        """ This function allow to define a WITH statement as prologue to the usual queries returned by query_get().
            It is useful if you need to shadow a table entirely and let the query_get work normally although you're
            fetching rows from your temporary table (built in the WITH statement) instead of the regular tables.

            @returns: the WITH statement to prepend to the sql query and the parameters used in that WITH statement
            @rtype: tuple(char, list)
        """
        sql = ''
        params = []

        #Cashflow Statement
        #------------------
        #The cash flow statement has a dedicated query because because we want to make a complex selection of account.move.line,
        #but keep simple to configure the financial report lines.
        if financial_report == self.env.ref('ohada_reports.account_financial_report_ohada_cashflow'):
            # Get all available fields from account_move_line, to build the 'select' part of the query
            replace_columns = {
                'date': 'ref.date',
                'debit': 'CASE WHEN \"account_move_line\".debit > 0 THEN ref.matched_percentage * \"account_move_line\".debit ELSE 0 END AS debit',
                'credit': 'CASE WHEN \"account_move_line\".credit > 0 THEN ref.matched_percentage * \"account_move_line\".credit ELSE 0 END AS credit',
                'balance': 'ref.matched_percentage * \"account_move_line\".balance AS balance'
            }
            columns = []
            columns_2 = []
            for name, field in self.env['account.move.line']._fields.items():
                if not(field.store and field.type not in ('one2many', 'many2many')):
                    continue
                columns.append('\"account_move_line\".\"%s\"' % name)
                if name in replace_columns:
                    columns_2.append(replace_columns.get(name))
                else:
                    columns_2.append('\"account_move_line\".\"%s\"' % name)
            select_clause_1 = ', '.join(columns)
            select_clause_2 = ', '.join(columns_2)

            # Get moves having a line using a bank account in one of the selected journals.
            if self.env.context.get('journal_ids'):
                bank_journals = self.env['account.journal'].browse(self.env.context.get('journal_ids'))
            else:
                bank_journals = self.env['account.journal'].search([('type', 'in', ('bank', 'cash'))])
            bank_accounts = bank_journals.mapped('default_debit_account_id') + bank_journals.mapped('default_credit_account_id')

            self._cr.execute('SELECT DISTINCT(move_id) FROM account_move_line WHERE account_id IN %s', [tuple(bank_accounts.ids)])
            bank_move_ids = tuple([r[0] for r in self.env.cr.fetchall()])

            # Avoid crash if there's no bank moves to consider
            if not bank_move_ids:
                return '''
                WITH account_move_line AS (
                    SELECT ''' + select_clause_1 + '''
                    FROM account_move_line
                    WHERE False)''', []

            # Fake domain to always get the join to the account_move_line__move_id table.
            fake_domain = [('move_id.id', '!=', None)]
            sub_tables, sub_where_clause, sub_where_params = self.env['account.move.line']._query_get(domain=fake_domain)
            tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=fake_domain + ast.literal_eval(self.domain))

            # Get moves having a line using a bank account.
            bank_journals = self.env['account.journal'].search([('type', 'in', ('bank', 'cash'))])
            bank_accounts = bank_journals.mapped('default_debit_account_id') + bank_journals.mapped('default_credit_account_id')
            q = '''SELECT DISTINCT(\"account_move_line\".move_id)
                    FROM ''' + tables + '''
                    WHERE account_id IN %s
                    AND ''' + sub_where_clause
            p = [tuple(bank_accounts.ids)] + sub_where_params
            self._cr.execute(q, p)
            bank_move_ids = tuple([r[0] for r in self.env.cr.fetchall()])

            # Only consider accounts related to a bank/cash journal, not all liquidity accounts
            if self.code in ('CASHEND', 'CASHSTART'):       #   , '_ZA', '_ZH'):    #E
                return '''
                WITH account_move_line AS (
                    SELECT ''' + select_clause_1 + '''
                    FROM account_move_line
                    WHERE account_id in %s)''', [tuple(bank_accounts.ids)]

            # Avoid crash if there's no bank moves to consider
            if not bank_move_ids:
                return '''
                WITH account_move_line AS (
                    SELECT ''' + select_clause_1 + '''
                    FROM account_move_line
                    WHERE False)''', []

            # The following query is aliasing the account.move.line table to consider only the journal entries where, at least,
            # one line is touching a liquidity account. Counterparts are either shown directly if they're not reconciled (or
            # not reconciliable), either replaced by the accounts of the entries they're reconciled with.
            sql = '''
                WITH account_move_line AS (

                    -- Part for the reconciled journal items
                    -- payment_table will give the reconciliation rate per account per move to consider
                    -- (so that an invoice with multiple payment terms would correctly display the income
                    -- accounts at the prorata of what hass really been paid)
                    WITH payment_table AS (
                        SELECT
                            aml2.move_id AS matching_move_id,
                            aml2.account_id,
                            aml.date AS date,
                            SUM(CASE WHEN (aml.balance = 0 OR sub.total_per_account = 0)
                                THEN 0
                                ELSE part.amount / sub.total_per_account
                            END) AS matched_percentage
                        FROM account_partial_reconcile part
                        LEFT JOIN account_move_line aml ON aml.id = part.debit_move_id
                        LEFT JOIN account_move_line aml2 ON aml2.id = part.credit_move_id
                        LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account FROM account_move_line GROUP BY move_id, account_id) sub ON (aml2.account_id = sub.account_id AND sub.move_id=aml2.move_id)
                        LEFT JOIN account_account acc ON aml.account_id = acc.id
                        WHERE part.credit_move_id = aml2.id
                        AND acc.reconcile
                        AND aml.move_id IN %s
                        GROUP BY aml2.move_id, aml2.account_id, aml.date

                        UNION ALL

                        SELECT
                            aml2.move_id AS matching_move_id,
                            aml2.account_id,
                            aml.date AS date,
                            SUM(CASE WHEN (aml.balance = 0 OR sub.total_per_account = 0)
                                THEN 0
                                ELSE part.amount / sub.total_per_account
                            END) AS matched_percentage
                        FROM account_partial_reconcile part
                        LEFT JOIN account_move_line aml ON aml.id = part.credit_move_id
                        LEFT JOIN account_move_line aml2 ON aml2.id = part.debit_move_id
                        LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account FROM account_move_line GROUP BY move_id, account_id) sub ON (aml2.account_id = sub.account_id AND sub.move_id=aml2.move_id)
                        LEFT JOIN account_account acc ON aml.account_id = acc.id
                        WHERE part.debit_move_id = aml2.id
                        AND acc.reconcile
                        AND aml.move_id IN %s
                        GROUP BY aml2.move_id, aml2.account_id, aml.date
                    )

                    SELECT ''' + select_clause_2 + '''
                    FROM account_move_line "account_move_line"
                    RIGHT JOIN payment_table ref ON ("account_move_line".move_id = ref.matching_move_id)
                    WHERE "account_move_line".account_id NOT IN (SELECT account_id FROM payment_table)
                    AND "account_move_line".move_id NOT IN %s

                    UNION ALL

                    -- Part for the unreconciled journal items.
                    -- Using amount_residual if the account is reconciliable is needed in case of partial reconciliation

                    SELECT ''' + select_clause_1.replace('"account_move_line"."balance_cash_basis"', 'CASE WHEN acc.reconcile THEN  "account_move_line".amount_residual ELSE "account_move_line".balance END AS balance_cash_basis') + '''
                    FROM account_move_line "account_move_line"
                    LEFT JOIN account_account acc ON "account_move_line".account_id = acc.id
                    WHERE "account_move_line".move_id IN %s
                    AND "account_move_line".account_id NOT IN %s
                )
            '''
            params = [tuple(bank_move_ids)] + [tuple(bank_move_ids)] + [tuple(bank_move_ids)] + [tuple(bank_move_ids)] + [tuple(bank_accounts.ids)]
        elif self.env.context.get('cash_basis'):
            #Cash basis option
            #-----------------
            #In cash basis, we need to show amount on income/expense accounts, but only when they're paid AND under the payment date in the reporting, so
            #we have to make a complex query to join aml from the invoice (for the account), aml from the payments (for the date) and partial reconciliation
            #(for the reconciled amount).
            user_types = self.env['account.account.type'].search([('type', 'in', ('receivable', 'payable'))])
            if not user_types:
                return sql, params

            # Get all columns from account_move_line using the psql metadata table in order to make sure all columns from the account.move.line model
            # are present in the shadowed table.
            sql = "SELECT column_name FROM information_schema.columns WHERE table_name='account_move_line'"
            self.env.cr.execute(sql)
            columns = []
            columns_2 = []
            replace_columns = {'date': 'ref.date',
                                'debit_cash_basis': 'CASE WHEN aml.debit > 0 THEN ref.matched_percentage * aml.debit ELSE 0 END AS debit_cash_basis',
                                'credit_cash_basis': 'CASE WHEN aml.credit > 0 THEN ref.matched_percentage * aml.credit ELSE 0 END AS credit_cash_basis',
                                'balance_cash_basis': 'ref.matched_percentage * aml.balance AS balance_cash_basis'}
            for field in self.env.cr.fetchall():
                field = field[0]
                columns.append("\"account_move_line\".\"%s\"" % (field,))
                if field in replace_columns:
                    columns_2.append(replace_columns.get(field))
                else:
                    columns_2.append('aml.\"%s\"' % (field,))
            select_clause_1 = ', '.join(columns)
            select_clause_2 = ', '.join(columns_2)

            #we use query_get() to filter out unrelevant journal items to have a shadowed table as small as possible
            tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=self._get_aml_domain())
            sql = """WITH account_move_line AS (
              SELECT """ + select_clause_1 + """
               FROM """ + tables + """
               WHERE (\"account_move_line\".journal_id IN (SELECT id FROM account_journal WHERE type in ('cash', 'bank'))
                 OR \"account_move_line\".move_id NOT IN (SELECT DISTINCT move_id FROM account_move_line WHERE user_type_id IN %s))
                 AND """ + where_clause + """
              UNION ALL
              (
               WITH payment_table AS (
                 SELECT aml.move_id, \"account_move_line\".date,
                        CASE WHEN (aml.balance = 0 OR sub_aml.total_per_account = 0)
                            THEN 0
                            ELSE part.amount / ABS(sub_aml.total_per_account)
                        END as matched_percentage
                   FROM account_partial_reconcile part
                   LEFT JOIN account_move_line aml ON aml.id = part.debit_move_id
                   LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account
                                FROM account_move_line
                                GROUP BY move_id, account_id) sub_aml
                            ON (aml.account_id = sub_aml.account_id AND sub_aml.move_id=aml.move_id)
                   LEFT JOIN account_move am ON aml.move_id = am.id, """ + tables + """
                   WHERE part.credit_move_id = "account_move_line".id
                    AND "account_move_line".user_type_id IN %s
                    AND """ + where_clause + """
                 UNION ALL
                 SELECT aml.move_id, \"account_move_line\".date,
                        CASE WHEN (aml.balance = 0 OR sub_aml.total_per_account = 0)
                            THEN 0
                            ELSE part.amount / ABS(sub_aml.total_per_account)
                        END as matched_percentage
                   FROM account_partial_reconcile part
                   LEFT JOIN account_move_line aml ON aml.id = part.credit_move_id
                   LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account
                                FROM account_move_line
                                GROUP BY move_id, account_id) sub_aml
                            ON (aml.account_id = sub_aml.account_id AND sub_aml.move_id=aml.move_id)
                   LEFT JOIN account_move am ON aml.move_id = am.id, """ + tables + """
                   WHERE part.debit_move_id = "account_move_line".id
                    AND "account_move_line".user_type_id IN %s
                    AND """ + where_clause + """
               )
               SELECT """ + select_clause_2 + """
                FROM account_move_line aml
                RIGHT JOIN payment_table ref ON aml.move_id = ref.move_id
                WHERE journal_id NOT IN (SELECT id FROM account_journal WHERE type in ('cash', 'bank'))
                  AND aml.move_id IN (SELECT DISTINCT move_id FROM account_move_line WHERE user_type_id IN %s)
              )
            ) """
            params = [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)]
        return sql, params

    def _compute_line(self, currency_table, financial_report, group_by=None, domain=[]):
        """ Computes the sum that appeas on report lines when they aren't unfolded. It is using _query_get() function
            of account.move.line which is based on the context, and an additional domain (the field domain on the report
            line) to build the query that will be used.

            @param currency_table: dictionary containing the foreign currencies (key) and their factor (value)
                compared to the current user's company currency
            @param financial_report: browse_record of the financial report we are willing to compute the lines for
            @param group_by: used in case of conditionnal sums on the report line
            @param domain: domain on the report line to consider in the query_get() call

            @returns : a dictionnary that has for each aml in the domain a dictionnary of the values of the fields
        """
        domain = domain and ast.literal_eval(ustr(domain))
        for index, condition in enumerate(domain):
            if condition[0].startswith('tax_ids.'):
                new_condition = (condition[0].partition('.')[2], condition[1], condition[2])
                taxes = self.env['account.tax'].with_context(active_test=False).search([new_condition])
                domain[index] = ('tax_ids', 'in', taxes.ids)
        tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=self._get_aml_domain())
        if financial_report.tax_report:
            where_clause += ''' AND "account_move_line".tax_exigible = 't' '''

        line = self
        financial_report = False

        while(not financial_report):
            financial_report = line.financial_report_id
            if not line.parent_id:
                break
            line = line.parent_id

        sql, params = self._get_with_statement(financial_report)

        select, select_params = self._query_get_select_sum(currency_table)
        where_params = params + select_params + where_params

        if (self.env.context.get('sum_if_pos') or self.env.context.get('sum_if_neg')) and group_by:
            sql = sql + "SELECT account_move_line." + group_by + " as " + group_by + "," + select + " FROM " + tables + " WHERE " + where_clause + " GROUP BY account_move_line." + group_by
            self.env.cr.execute(sql, where_params)
            res = {'balance': 0, 'debit': 0, 'credit': 0, 'amount_residual': 0}
            for row in self.env.cr.dictfetchall():
                if (row['balance'] > 0 and self.env.context.get('sum_if_pos')) or (row['balance'] < 0 and self.env.context.get('sum_if_neg')):
                    for field in ['debit', 'credit', 'balance', 'amount_residual']:
                        res[field] += row[field]
            res['currency_id'] = self.env.user.company_id.currency_id.id
            return res

        sql = sql + "SELECT " + select + " FROM " + tables + " WHERE " + where_clause
        self.env.cr.execute(sql, where_params)
        results = self.env.cr.dictfetchall()[0]
        results['currency_id'] = self.env.user.company_id.currency_id.id
        return results

    @api.multi
    def _compute_date_range(self):
        '''Compute the current report line date range according to the dates passed through the context
        and its specified special_date_changer.

        :return: The date_from, date_to, strict_range values to consider for the report line.
        '''
        date_from = self._context.get('date_from', False)
        date_to = self._context.get('date_to', False)

        strict_range = self.special_date_changer == 'strict_range'
        if self.special_date_changer == 'from_beginning':
            date_from = False
        if self.special_date_changer == 'to_beginning_of_period' and date_from:
            date_tmp = fields.Date.from_string(self._context['date_from']) - relativedelta(days=1)
            date_to = date_tmp.strftime('%Y-%m-%d')
            if date_from:                                                                                   #E+
                date_tmp = fields.Date.from_string(self._context['date_from']) - relativedelta(years=1)     #E+
                date_from = date_tmp.strftime('%Y-%m-%d')                                                   #E+
            #date_from = False                                                                              #E-
        if self.special_date_changer == 'from_fiscalyear' and date_to:
            date_tmp = fields.Date.from_string(date_to)
            date_tmp = self.env.user.company_id.compute_fiscalyear_dates(date_tmp)['date_from']
            date_from = date_tmp.strftime('%Y-%m-%d')
            strict_range = True
        return date_from, date_to, strict_range

    @api.multi
    def report_move_lines_action(self):
        domain = ast.literal_eval(self.domain)
        if 'date_from' in self.env.context.get('context', {}):
            if self.env.context['context'].get('date_from'):
                domain = expression.AND([domain, [('date', '>=', self.env.context['context']['date_from'])]])
            if self.env.context['context'].get('date_to'):
                domain = expression.AND([domain, [('date', '<=', self.env.context['context']['date_to'])]])
            if self.env.context['context'].get('state', 'all') == 'posted':
                domain = expression.AND([domain, [('move_id.state', '=', 'posted')]])
            if self.env.context['context'].get('company_ids'):
                domain = expression.AND([domain, [('company_id', 'in', self.env.context['context']['company_ids'])]])
        return {'type': 'ir.actions.act_window',
                'name': 'Journal Items (%s)' % self.name,
                'res_model': 'account.move.line',
                'view_mode': 'tree,form',
                'domain': domain,
                }

    @api.one
    @api.constrains('groupby')
    def _check_same_journal(self):
        if self.groupby and self.groupby not in self.env['account.move.line']:
            raise ValidationError(_("Groupby should be a journal item field"))

    def _get_sum(self, currency_table, financial_report, field_names=None):
        ''' Returns the sum of the amls in the domain '''
        if not field_names:
            field_names = ['debit', 'credit', 'balance', 'amount_residual']
        res = dict((fn, 0.0) for fn in field_names)
        if self.domain:
            date_from, date_to, strict_range = \
                self._compute_date_range()
            res = self.with_context(strict_range=strict_range, date_from=date_from, date_to=date_to, active_test=False)._compute_line(currency_table, financial_report, group_by=self.groupby, domain=self._get_aml_domain())
        return res

    @api.one
    def _get_balance(self, linesDict, currency_table, financial_report, field_names=None):
        if not field_names:
            field_names = ['debit', 'credit', 'balance']
        res = dict((fn, 0.0) for fn in field_names)
        c = FormulaContext(self.env['ohada.financial.html.report.line'], linesDict, currency_table, financial_report, self)
        if self.formulas:
            for f in self.formulas.split(';'):
                [field, formula] = f.split('=')
                field = field.strip()
                if field in field_names:
                    try:
                        res[field] = safe_eval(formula, c, nocopy=True)
                    except ValueError as err:
                        if 'division by zero' in err.args[0]:
                            res[field] = 0
                        else:
                            raise err
        return res

    def _get_rows_count(self):
        groupby = self.groupby or 'id'
        if groupby not in self.env['account.move.line']:
            raise ValueError(_('Groupby should be a field from account.move.line'))

        date_from, date_to, strict_range = self._compute_date_range()
        tables, where_clause, where_params = self.env['account.move.line'].with_context(strict_range=strict_range,
                                                                                        date_from=date_from,
                                                                                        date_to=date_to)._query_get(domain=self._get_aml_domain())

        query = 'SELECT count(distinct(account_move_line.' + groupby + ')) FROM ' + tables + 'WHERE' + where_clause
        self.env.cr.execute(query, where_params)
        return self.env.cr.dictfetchall()[0]['count']

    def _get_value_from_context(self):
        if self.env.context.get('financial_report_line_values'):
            return self.env.context.get('financial_report_line_values').get(self.code, 0)
        return 0

    def _format(self, value):
        '''
            Reason for modifying this module: in OHADA reports, the currency is not displayed, all amounts must be reported in XOF
            TODO: if currency is not XOF, we need to convert the value
        '''
        if self.env.context.get('no_format'):
            return value
        value['no_format_name'] = value['name']
        if self.figure_type == 'float':
            currency_id = self.env.user.company_id.currency_id
            if currency_id.is_zero(value['name']):
                # don't print -0.0 in reports
                value['name'] = abs(value['name'])
                value['class'] = 'number'
            if not currency_id or (currency_id and (currency_id.name != 'XOF' or currency_id.symbol == 'CFA')): #E+
                value['name'] = formatLang(self.env, value['name'], digits=0)                                   #E+
            else: #E+   
                #E: TODO: Here we need to convert the value to XOF
                value['name'] = formatLang(self.env, value['name'], currency_obj=currency_id)
            return value
        if self.figure_type == 'percents':
            value['name'] = str(round(value['name'] * 100, 1)) + '%'
            return value
        value['name'] = round(value['name'], 1)
        return value

    def _get_gb_name(self, gb_id):
        if self.groupby and self.env['account.move.line']._fields[self.groupby].relational:
            relation = self.env['account.move.line']._fields[self.groupby].comodel_name
            gb = self.env[relation].browse(gb_id)
            return gb.name_get()[0][1] if gb and gb.exists() else _('Undefined')
        return gb_id

    def _build_cmp(self, balance, comp):
        if comp != 0:
            res = round((balance - comp) / comp * 100, 1)
            # In case the comparison is made on a negative figure, the color should be the other
            # way around. For example:
            #                       2018         2017           %
            # Product Sales      1000.00     -1000.00     -200.0%
            #
            # The percentage is negative, which is mathematically correct, but my sales increased
            # => it should be green, not red!
            if (res > 0) != (self.green_on_positive and comp > 0):
                return {'name': str(res) + '%', 'class': 'number color-red'}
            else:
                return {'name': str(res) + '%', 'class': 'number color-green'}
        else:
            return {'name': _('n/a')}

    def _build_abs(self, balance, comp):
        res = round(balance - comp)
        if (res > 0) != (self.green_on_positive and comp > 0):
            return {'name': str(res), 'class': 'number color-red'}
        else:
            return {'name': str(res), 'class': 'number color-green'}

    def _split_formulas(self):

        result = {}
        if self.formulas:
            for f in self.formulas.split(';'):
                [column, formula] = f.split('=')
                column = column.strip()
                result.update({column: formula})
        return result

    def _get_aml_domain(self):
        return (safe_eval(self.domain) or []) + (self._context.get('filter_domain') or []) + (self._context.get('group_domain') or [])

    def _get_group_domain(self, group, groups):
        return [(field, '=', grp) for field, grp in izip(groups['fields'], group)]

    def _eval_formula(self, financial_report, debit_credit, currency_table, linesDict_per_group, groups=False):
        groups = groups or {'fields': [], 'ids': [()]}
        debit_credit = debit_credit and financial_report.debit_credit
        formulas = self._split_formulas()
        currency = self.env.user.company_id.currency_id

        line_res_per_group = []

        if not groups['ids']:
            return [{'line': {'balance': 0.0}}]

        # this computes the results of the line itself
        for group_index, group in enumerate(groups['ids']):
            self_for_group = self.with_context(group_domain=self._get_group_domain(group, groups))
            linesDict = linesDict_per_group[group_index]
            line = False

            if self.code and self.code in linesDict:
                line = linesDict[self.code]
            elif formulas and formulas['balance'].strip() == 'count_rows' and self.groupby:
                line_res_per_group.append({'line': {'balance': self_for_group._get_rows_count()}})
            elif formulas and formulas['balance'].strip() == 'from_context':
                line_res_per_group.append({'line': {'balance': self_for_group._get_value_from_context()}})
            else:
                line = FormulaLine(self_for_group, currency_table, financial_report, linesDict=linesDict)

            if line:
                res = {}
                res['balance'] = line.balance
                res['balance'] = currency.round(line.balance)
                if debit_credit:
                    res['credit'] = currency.round(line.credit)
                    res['debit'] = currency.round(line.debit)
                line_res_per_group.append(res)

        # don't need any groupby lines for count_rows and from_context formulas
        if all('line' in val for val in line_res_per_group):
            return line_res_per_group

        columns = []
        # this computes children lines in case the groupby field is set
        if self.domain and self.groupby and self.show_domain != 'never':
            if self.groupby not in self.env['account.move.line']:
                raise ValueError(_('Groupby should be a field from account.move.line'))

            groupby = [self.groupby or 'id']
            if groups:
                groupby = groups['fields'] + groupby
            groupby = ', '.join(['"account_move_line".%s' % field for field in groupby])

            aml_obj = self.env['account.move.line']
            tables, where_clause, where_params = aml_obj._query_get(domain=self._get_aml_domain())
            sql, params = self._get_with_statement(financial_report)
            if financial_report.tax_report:
                where_clause += ''' AND "account_move_line".tax_exigible = 't' '''

            select, select_params = self._query_get_select_sum(currency_table)
            params += select_params
            sql = sql + "SELECT " + groupby + ", " + select + " FROM " + tables + " WHERE " + where_clause + " GROUP BY " + groupby + " ORDER BY " + groupby

            params += where_params
            self.env.cr.execute(sql, params)
            results = self.env.cr.fetchall()
            for group_index, group in enumerate(groups['ids']):
                linesDict = linesDict_per_group[group_index]
                results_for_group = [result for result in results if group == result[:len(group)]]
                if results_for_group:
                    results_for_group = [r[len(group):] for r in results_for_group]
                    results_for_group = dict([(k[0], {'balance': k[1], 'amount_residual': k[2], 'debit': k[3], 'credit': k[4]}) for k in results_for_group])
                    c = FormulaContext(self.env['ohada.financial.html.report.line'].with_context(group_domain=self._get_group_domain(group, groups)),
                                       linesDict, currency_table, financial_report, only_sum=True)
                    if formulas:
                        for key in results_for_group:
                            c['sum'] = FormulaLine(results_for_group[key], currency_table, financial_report, type='not_computed')
                            c['sum_if_pos'] = FormulaLine(results_for_group[key]['balance'] >= 0.0 and results_for_group[key] or {'balance': 0.0},
                                                          currency_table, financial_report, type='not_computed')
                            c['sum_if_neg'] = FormulaLine(results_for_group[key]['balance'] <= 0.0 and results_for_group[key] or {'balance': 0.0},
                                                          currency_table, financial_report, type='not_computed')
                            for col, formula in formulas.items():
                                if col in results_for_group[key]:
                                    results_for_group[key][col] = safe_eval(formula, c, nocopy=True)
                    to_del = []
                    for key in results_for_group:
                        if self.env.user.company_id.currency_id.is_zero(results_for_group[key]['balance']):
                            to_del.append(key)
                    for key in to_del:
                        del results_for_group[key]
                    results_for_group.update({'line': line_res_per_group[group_index]})
                    columns.append(results_for_group)
                else:
                    res_vals = {'balance': 0.0}
                    if debit_credit:
                        res_vals.update({'debit': 0.0, 'credit': 0.0})
                    columns.append({'line': res_vals})

        return columns or [{'line': res} for res in line_res_per_group]

    def _put_columns_together(self, data, domain_ids):
        res = dict((domain_id, []) for domain_id in domain_ids)
        for period in data:
            debit_credit = False
            if 'debit' in period['line']:
                debit_credit = True
            for domain_id in domain_ids:
                if debit_credit:
                    res[domain_id].append(period.get(domain_id, {'debit': 0})['debit'])
                    res[domain_id].append(period.get(domain_id, {'credit': 0})['credit'])
                res[domain_id].append(period.get(domain_id, {'balance': 0})['balance'])
        return res

    def _divide_line(self, line):
        line1 = {
            'id': line['id'],
            'name': line['name'],
            'class': line['class'],
            'level': line['level'],
            'columns': [{'name': ''}] * len(line['columns']),
            'unfoldable': line['unfoldable'],
            'unfolded': line['unfolded'],
            'page_break': line['page_break'],
        }
        line2 = {
            'id': line['id'],
            'name': _('Total') + ' ' + line['name'],
            'class': 'total',
            'level': line['level'] + 1,
            'columns': line['columns'],
        }
        return [line1, line2]

    @api.multi
    def _get_lines(self, financial_report, currency_table, options, linesDicts):
        final_result_table = []
        comparison_table = [options.get('date')]
        comparison_table += options.get('comparison') and options['comparison'].get('periods', []) or []
        currency_precision = self.env.user.company_id.currency_id.rounding

        # build comparison table
        for line in self:
            res = []
            debit_credit = len(comparison_table) == 1
            # wdb.set_trace()
            if financial_report.code == 'BS1' and options['comparison']['filter'] == 'no_comparison':
                debit_credit = len(comparison_table) == 2
            domain_ids = {'line'}
            k = 0
            for period in comparison_table:
                date_from = period.get('date_from', False)
                date_to = period.get('date_to', False) or period.get('date', False)
                date_from, date_to, strict_range = line.with_context(date_from=date_from, date_to=date_to)._compute_date_range()

                r = line.with_context(date_from=date_from,
                                      date_to=date_to,
                                      strict_range=strict_range)._eval_formula(financial_report,
                                                                               debit_credit,
                                                                               currency_table,
                                                                               linesDicts[k],
                                                                               groups=options.get('groups'))
                debit_credit = False
                res.extend(r)
                for column in r:
                    domain_ids.update(column)
                k += 1

            res = line._put_columns_together(res, domain_ids)

            if line.hidden_line:                   
                continue
            if line.hide_if_zero and all([float_is_zero(k, precision_rounding=currency_precision) for k in res['line']]):
                continue

            # Post-processing ; creating line dictionnary, building comparison, computing total for extended, formatting
            vals = {
                'id': line.id,
                'name': line.name,
                'reference': line.reference,       
                'note': line.note,
                'note_id': line.note_id,
                'symbol': line.symbol,
                'level': line.level,
                'class': '',
                'columns': [{'name': l} for l in res['line']],
                'unfoldable': len(domain_ids) > 1 and line.show_domain != 'always',
                'unfolded': line.id in options.get('unfolded_lines', []) or line.show_domain == 'always',
                'page_break': line.print_on_new_page,
                'letter': line.letter,
                'header': line.header,
                'table_spacer': line.table_spacer,          #E?
                'colspan': line.colspan,
                'rowspan': line.rowspan,
                'sequence': line.sequence,
            }

            # wdb.set_trace()
            if financial_report.tax_report and line.domain and not line.action_id:
                vals['caret_options'] = 'tax.report.line'

            if line.action_id:
                vals['action_id'] = line.action_id.id
            domain_ids.remove('line')
            lines = [vals]
            groupby = line.groupby or 'aml'

            if line.id in options.get('unfolded_lines', []) or line.show_domain == 'always':
                if line.groupby:
                    domain_ids = sorted(list(domain_ids), key=lambda k: line._get_gb_name(k))
                for domain_id in domain_ids:
                    name = line._get_gb_name(domain_id)
                    if not self.env.context.get('print_mode') or not self.env.context.get('no_format'):
                        name = name[:40] + '...' if name and len(name) >= 45 else name
                    vals = {
                        'id': domain_id,
                        'name': name,
                        'level': line.level,
                        'parent_id': line.id,
                        'columns': [{'name': l} for l in res[domain_id]],
                        'caret_options': groupby == 'account_id' and 'account.account' or groupby,
                        'financial_group_line_id': line.id,
                    }
                    if line.financial_report_id.name == 'Aged Receivable':
                        vals['trust'] = self.env['res.partner'].browse([domain_id]).trust
                    lines.append(vals)
            # ==================== test generate values with new models ===============================================
            if line.columns_id:
                if not line.columns_id.line_name:
                    del lines[0]['name']
                lines[0]['columns'] = []
                if line.columns_id.cell_id:
                    for i in line.columns_id.cell_id:
                        lines[0]['columns'].append({
                            'name': [i.name] if line.header else i.name,
                            'colspan': i.colspan,
                            'rowspan': i.rowspan,
                            'rotate': i.rotate,
                        })
                else:
                    pass
                result = lines
            elif financial_report.default_columns_quantity:
                lines[0]['columns'] = []
                for i in range(financial_report.default_columns_quantity):
                    lines[0]['columns'].append({'name': ' '})
                result = lines
            # =========================================================================================================
            else:
                for vals in lines:
                    if len(comparison_table) == 2 and options['comparison']['filter'] == 'no_comparison':
                        for i in range(len(vals['columns'])):
                            vals['columns'][i] = line._format(vals['columns'][i])
                    elif len(comparison_table) == 2 and not options.get('groups'):
                        if financial_report.code in ['N15A', 'N16A', 'N18', 'N19'] and line.header is not True:
                            vals['columns'].append(line._build_abs(vals['columns'][0]['name'], vals['columns'][1]['name']))
                            vals['columns'].append(line._build_cmp(vals['columns'][0]['name'], vals['columns'][1]['name']))
                            for i in [0, 1]:
                                vals['columns'][i] = line._format(vals['columns'][i])
                        else:
                            vals['columns'].append(line._build_cmp(vals['columns'][0]['name'], vals['columns'][1]['name']))
                            for i in [0, 1]:
                                vals['columns'][i] = line._format(vals['columns'][i])
                    else:
                        vals['columns'] = [line._format(v) for v in vals['columns']]
                    if not line.formulas:
                        vals['columns'] = [{'name': ''} for k in vals['columns']]
                if line.reference == 'REF':
                    vals['columns'][0]['name'] = ['EXERCICE', 'au 31/12/' + line._context['date_to'][0:4]]
                    if financial_report.code == 'BS1' and options['comparison']['filter'] == 'no_comparison':
                        vals['columns'][1]['name'] = ['EXERCICE', 'au 31/12/' + line._context['periods'][0]['string'][-4:]]
                        del vals['columns'][3]
                        del vals['columns'][2]
                        vals['colspan0'] = 3
                    elif len(vals['columns']) > 1 and line._context.get('periods') != None \
                            and options['comparison']['filter'] == 'no_comparison' or len(options['comparison']['periods']) > 1:
                        for i in range(len(vals['columns'][1:])):
                            vals['columns'][i+1]['name'] = ['EXERCICE', 'au 31/12/' + line._context['periods'][i]['string'][-4:]]
                    elif len(vals['columns']) > 1 and line._context.get('periods') != None:
                        for i in range(len(vals['columns'][1:])-1):
                            vals['columns'][i+1]['name'] = ['EXERCICE', 'au 31/12/' + line._context['periods'][i]['string'][-4:]]
                elif line.header == True and financial_report.type == 'note':
                    if financial_report.code == "N1" and line.sequence == 1:
                        vals['columns'][0]['name'] = ['Montant brut']
                        vals['columns'].append({'name': ['SURETES REELLES']})
                        vals['colspan0'] = 3
                    elif financial_report.code == "N3A" and line.sequence == 1:
                        header_list = [["MOUVEMENTS", "BRUTS À", "L'OUVERTURE", "DE L EXERCICE"],
                                       ["ACQUISITIONS,", "APPORTS,", "CREATIONS"],
                                       ["VIREMENTS DE", "POSTE À", "POSTE"],
                                       ["Suite à une", "réévaluation", "pratiquée au cours", "de l'exercice"],
                                       ["Cessions,", "scissions, hors-", "service"],
                                       ["Virements de", "poste à poste"],
                                       ["MOUVEMENTS", "BRUTS À LA", "CLÔTURE DE", "L'EXERCICE"]]
                        vals['columns'] = []
                        for i in range(len(header_list)):
                            vals['columns'].append({'name': header_list[i]})
                    elif financial_report.code == "N3B" and line.sequence == 1:
                        vals['name'] = ['LIBELLES']
                        vals['columns'] = [{'name': ["NATURE DU", "CONTRAT", "(I ; M ; A) [1]"], 'colspan': 1, 'rowspan': 2},
                                           {'name': ["A"], 'colspan': 1, 'rowspan': 1},
                                           {'name': ["AUGMENTATIONS  B"], 'colspan': 3, 'rowspan': 1},
                                           {'name': ["DIMINUTIONS  B"], 'colspan': 2, 'rowspan': 1},
                                           {'name': ["D = A + B - C"], 'colspan': 1, 'rowspan': 1}]
                    elif financial_report.code == "N3B" and line.sequence == 2:
                        vals['name'] = ["MOUVEMENTS", "BRUTS À", "L'OUVERTURE", "DE L EXERCICE"]
                        subheader_list = [
                                         ["ACQUISITIONS,", "APPORTS,", "CREATIONS"],
                                         ["VIREMENTS DE", "POSTE À", "POSTE"],
                                         ["Suite à une", "réévaluation", "pratiquée au cours", "de l'exercice"],
                                         ["Cessions,", "scissions, hors-", "service"],
                                         ["Virements de", "poste à poste"],
                                         ["MOUVEMENTS", "BRUTS À LA", "CLÔTURE DE", "L'EXERCICE"]]
                        vals['columns'] = []
                        for i in range(len(subheader_list)):
                            vals['columns'].append({'name': subheader_list[i]})
                    elif financial_report.code == "N3C" and line.sequence == 1:
                        vals['name'] = ['LIBELLES']
                        header_list = [["A"],
                                       ["B"],
                                       ["C"],
                                       ["D = A + B - C"]]
                        vals['columns'] = []
                        for i in range(len(header_list)):
                            vals['columns'].append({'name': header_list[i]})
                    elif financial_report.code == "N3C" and line.sequence == 2:
                        vals['name'] = ["AMORTISSEMENTS", "CUMULES À", "L'OUVERTURE DE", "L'EXERCICE"]
                        subheader_list = [
                                          ["AUGMENTATIONS:", "DOTATIONS DE", "L'EXERCICE"],
                                          ["DIMINUTIONS:", "AMORTISSEMENTS", "RELATIFS AUX", "SORTIES DE", "L'ACTIF"],
                                          ["CUMULS DES", "AMORTISSEMENTS", "À LA CLÔTURE DE", "L'EXERCICE"]]
                        vals['columns'] = []
                        for i in range(len(subheader_list)):
                            vals['columns'].append({'name': subheader_list[i]})
                    elif financial_report.code == "N3D" and line.sequence == 1:
                        vals['name'] = ['LIBELLES']
                        header_list = [["MONTANT BRUT"],
                                       ["AMORTISSEMENTS", "PRATIQUES"],
                                       ["VALEUR", "COMPTABLE", "NETTE"],
                                       ["PRIX DE CESSION"],
                                       ["PLUS-VALUE", "OU", "MOINS-VALUE"]]
                        vals['columns'] = []
                        for i in range(len(header_list)):
                            vals['columns'].append({'name': header_list[i]})
                    elif financial_report.code == "N3E" and line.sequence == 2:
                        header_list = [["Montants côuts historiques"],
                                       ["Amortissements supplémentaires"]]
                        vals['columns'] = []
                        for i in range(len(header_list)):
                            vals['columns'].append({'name': header_list[i]})
                    elif (financial_report.code == "N16BB" or financial_report.code == "N16BB_1") and line.sequence == 1:
                        vals['name'] = "DUMMY LINE NAME"
                        vals['columns'] = []
                    elif financial_report.code == "N32" and line.sequence in [1, 2]:
                        header_list = [["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"],
                                       ["DUMMY LINE NAME"]]
                        vals['columns'] = []
                        for i in range(len(header_list)):
                            vals['columns'].append({'name': header_list[i]})
                    elif line.sequence == 1 or ((financial_report.code == "N16BB" or financial_report.code == "N16BB_1") and line.sequence == 2):
                        vals['columns'][0]['name'] = ['ANNEE ' + line._context['date_from'][0:4]]
                        if len(vals['columns']) > 1 and line._context.get('periods') != None \
                                and options['comparison']['filter'] == 'no_comparison' or len(
                            options['comparison']['periods']) > 1:
                            for i in range(len(vals['columns'][1:])):
                                vals['columns'][i + 1]['name'] = ['ANNEE ' + line._context['periods'][i]['string']]
                            if financial_report.code != "N31":
                                vals['columns'][- 1]['name'] = ['Variation en %']
                        elif len(vals['columns']) > 1 and line._context.get('periods') != None:
                            for i in range(len(vals['columns'][1:]) - 1):
                                vals['columns'][i + 1]['name'] = ['ANNEE ' + line._context['periods'][i]['string']]
                            if financial_report.code in ['N15A', 'N16A', 'N18', 'N19']:
                                vals['columns'][- 1]['name'] = ['Variation en valeur', 'absolue']
                                vals['columns'].append({'name': ['Variation en %']})
                            else:
                                vals['columns'][- 1]['name'] = ['Variation en %']

                # ============= For Notes 4, 7, 8, 17, 15A, 16A, 18, 19 =====================

                if line.header is True and financial_report.code in ['N4', 'N7', 'N8', 'N17', 'N15A', 'N16A', 'N18', 'N19'] and len(comparison_table) == 2:
                    header_list = [["Créances à un", "an au plus"], ["Créances à plus", "d'un an à deux", "ans au plus"],
                                   ["Créances à plus", "de deux ans au", "plus"]]
                    for i in header_list:
                        vals['columns'].append({'name': i})
                elif line.header is True and financial_report.code in ['N15B'] and len(comparison_table) == 2:
                    header_list = [["Régime fiscale"], ["Échéance"]]
                    for i in header_list:
                        vals['columns'].append({'name': i})
                elif financial_report.code in ['N4', 'N7', 'N8', 'N17', 'N15A', 'N16A', 'N18', 'N19'] and len(comparison_table) == 2:
                    amount_of_periods = 4
                    amount_of_group_ids = len(options.get('groups', {}).get('ids') or []) or 1
                    linesDicts = [[{} for _ in range(0, amount_of_group_ids)] for _ in range(0, amount_of_periods)]
                    comparison_table = [options.get('date')]
                    comparison_table += options.get('comparison') and options['comparison'].get('periods', []) or []
                    for i in range(3):
                        date_from = str(int(options.get('date')['string']) - (i + 1)) + '-01-01'
                        date_to = str(int(options.get('date')['string']) - (i + 1)) + '-12-31'
                        date_from, date_to, strict_range = line.with_context(date_from=date_from,
                                                                             date_to=date_to)._compute_date_range()

                        r = line.with_context(date_from=date_from,
                                              date_to=date_to,
                                              strict_range=strict_range)._eval_formula(financial_report,
                                                                                       debit_credit,
                                                                                       currency_table,
                                                                                       linesDicts[k],
                                                                                       groups=options.get('groups'))

                        vals['columns'].append(line._format({'name': r[0]['line']['balance']}))
                elif financial_report.code in ['N15B'] and len(comparison_table) == 2:
                    vals['columns'].append({'name': " "})
                    vals['columns'].append({'name': " "})


                if line.header is True and financial_report.type == 'note' and financial_report.code == 'N4_1':
                    vals['columns'] = []
                    header_list = [["Localisation", "(Ville/Pays)"], ["Valeur" ,"d'acquisition"], ["% détenu"],
                                   ["Montants des", "capitaux propres", "filiale"], ["Résultat dernier", "exercice filiale"]]

                    for i in header_list:
                        vals['columns'].append({'name': i})
                elif financial_report.type == 'note' and financial_report.code == 'N4_1':
                    for i in range(2):
                        vals['columns'].append({'name': ' '})

                # ===============================================================

                if len(lines) == 1:
                    new_lines = line.children_ids._get_lines(financial_report, currency_table, options, linesDicts)
                    if new_lines and line.formulas:
                        result = [lines[0]] + new_lines
                    else:
                        result = lines + new_lines
                else:
                    result = lines
                if line.note_report_ids:
                    line.note_id = str(self.env['ir.actions.client'].search([('name', '=', line.note_report_ids.name)]).id)
                if result[0]['note'] == 'NET':
                    if financial_report.code == 'BS1' and options['comparison']['filter'] == 'no_comparison':
                        result[0]['columns'][0]['name'] = 'BRUT'
                        result[0]['columns'][1]['name'] = 'AMORT. ET DEPREC.'
                        result[0]['columns'][2]['name'] = 'NET'
                        result[0]['columns'][3]['name'] = 'NET'
                    elif len(result[0]['columns']) > 1 and options['comparison']['filter'] == 'no_comparison' or \
                            len(options['comparison']['periods']) > 1:
                        for i in range(len(result[0]['columns'])):
                            result[0]['columns'][i]['name'] = 'NET'
                    elif len(result[0]['columns']) > 1:
                        for i in range(len(result[0]['columns']) - 1):
                            result[0]['columns'][i]['name'] = 'NET'
                        result[0]['columns'][-1]['name'] = '%'
                    else:
                        result[0]['columns'][0]['name'] = 'NET'

                # ==================== temporary solution for special notes =============================================
                if financial_report.type == 'note':
                    if financial_report.code == "N1" and line.sequence == 2:
                        del vals['note']
                        vals['name'] = 'Hypothèque'
                        vals['columns'][0]['name'] = 'Nantissements'
                        vals['columns'].append({'name': 'Gages/Autres'})
                    elif financial_report.code == 'N1' and line.sequence == 26:
                        vals['columns'].append({'name': ['Engagements', 'donnés']})
                        vals['columns'].append({'name': ['Engagements', 'recus']})
                    elif financial_report.code == 'N1' and line.sequence > 25:
                        vals['columns'].append({'name': ' '})
                        vals['columns'].append({'name': ' '})
                    elif financial_report.code == 'N1' and line.header is not True:
                        vals['columns'].append({'name': ' '})
                        vals['columns'].append({'name': ' '})
                        vals['columns'].append({'name': ' '})
                    elif financial_report.code in ['N2', "N35"]:
                        vals['columns'] = []
                    elif financial_report.code in ['N3A', 'N3B'] and line.sequence > 2:
                        vals['columns'] = []
                        for i in range(7):
                            vals['columns'].append({'name': ' '})
                    elif financial_report.code == 'N3C' and line.sequence > 2:
                        vals['columns'] = []
                        for i in range(4):
                            vals['columns'].append({'name': ' '})
                    elif (financial_report.code == 'N3D' and line.sequence > 2) or (financial_report.name in ['N13', 'N31'] and line.sequence > 1) or financial_report.name in ["N12", "N36"]:
                        vals['columns'] = []
                        for i in range(5):
                            vals['columns'].append({'name': ' '})
                    elif financial_report.code == 'N3E' and not line.sequence == 2:
                        vals['columns'] = []
                        for i in range(2):
                            vals['columns'].append({'name': ' '})
                    elif (financial_report.code in ["N16BB", "N16BB_1"] and line.sequence != 1) or financial_report.name in ["N16B", "N16B_1"]:
                        vals['columns'].pop()
                    elif financial_report.code in ["N32", "N27B"]:
                        vals['columns'] = []
                        for i in range(13):
                            vals['columns'].append({'name': ' '})
                    elif financial_report.code in ["N33", "N28", "N27B_1"]:
                        vals['columns'] = []
                        for i in range(8):
                            vals['columns'].append({'name': ' '})
                    elif financial_report.code == "N37":
                        vals['columns'] = []
                        vals['columns'].append({'name': ' '})
                    elif financial_report.code == 'N8A':
                        vals['columns'] = []
                        for i in range(3):
                            vals['columns'].append({'name': ' '})

            final_result_table += result

        return final_result_table


class FormulaLine(object):
    def __init__(self, obj, currency_table, financial_report, type='balance', linesDict=None):
        if linesDict is None:
            linesDict = {}
        fields = dict((fn, 0.0) for fn in ['debit', 'credit', 'balance'])
        if type == 'balance':
            fields = obj._get_balance(linesDict, currency_table, financial_report)[0]
            linesDict[obj.code] = self
        elif type in ['sum', 'sum_if_pos', 'sum_if_neg']:
            if type == 'sum_if_neg':
                obj = obj.with_context(sum_if_neg=True)
            if type == 'sum_if_pos':
                obj = obj.with_context(sum_if_pos=True)
            if obj._name == 'ohada.financial.html.report.line':
                fields = obj._get_sum(currency_table, financial_report)
                self.amount_residual = fields['amount_residual']
            elif obj._name == 'account.move.line':
                self.amount_residual = 0.0
                field_names = ['debit', 'credit', 'balance', 'amount_residual']
                res = obj.env['ohada.financial.html.report.line']._compute_line(currency_table, financial_report)
                for field in field_names:
                    fields[field] = res[field]
                self.amount_residual = fields['amount_residual']
        elif type == 'not_computed':
            for field in fields:
                fields[field] = obj.get(field, 0)
            self.amount_residual = obj.get('amount_residual', 0)
        elif type == 'null':
            self.amount_residual = 0.0
        self.balance = fields['balance']
        self.credit = fields['credit']
        self.debit = fields['debit']


class FormulaContext(dict):
    def __init__(self, reportLineObj, linesDict, currency_table, financial_report, curObj=None, only_sum=False, *data):
        self.reportLineObj = reportLineObj
        self.curObj = curObj
        self.linesDict = linesDict
        self.currency_table = currency_table
        self.only_sum = only_sum
        self.financial_report = financial_report
        return super(FormulaContext, self).__init__(data)

    def __getitem__(self, item):
        formula_items = ['sum', 'sum_if_pos', 'sum_if_neg']
        if item in set(__builtins__.keys()) - set(formula_items):
            return super(FormulaContext, self).__getitem__(item)

        if self.only_sum and item not in formula_items:
            return FormulaLine(self.curObj, self.currency_table, self.financial_report, type='null')
        if self.get(item):
            return super(FormulaContext, self).__getitem__(item)
        if self.linesDict.get(item):
            return self.linesDict[item]
        if item == 'sum':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum')
            self['sum'] = res
            return res
        if item == 'sum_if_pos':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum_if_pos')
            self['sum_if_pos'] = res
            return res
        if item == 'sum_if_neg':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum_if_neg')
            self['sum_if_neg'] = res
            return res
        if item == 'NDays':
            d1 = fields.Date.from_string(self.curObj.env.context['date_from'])
            d2 = fields.Date.from_string(self.curObj.env.context['date_to'])
            res = (d2 - d1).days
            self['NDays'] = res
            return res
        if item == 'count_rows':
            return self.curObj._get_rows_count()
        if item == 'from_context':
            return self.curObj._get_value_from_context()
        line_id = self.reportLineObj.search([('code', '=', item)], limit=1)
        if line_id:
            date_from, date_to, strict_range = line_id._compute_date_range()
            res = FormulaLine(line_id.with_context(strict_range=strict_range, date_from=date_from, date_to=date_to), self.currency_table, self.financial_report, linesDict=self.linesDict)
            self.linesDict[item] = res
            return res
        return super(FormulaContext, self).__getitem__(item)


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    @api.multi
    def _update_translations(self, filter_lang=None):
        """ Create missing translations after loading the one of ohada.financial.html.report

        Use the translations of the ohada.financial.html.report to translate the linked
        ir.actions.client and ir.ui.menu generated at the creation of the report
        """
        res = super(IrModuleModule, self)._update_translations(filter_lang=filter_lang)

        # generated missing action translations for translated reports
        self.env.cr.execute("""
           INSERT INTO ir_translation (lang, type, name, res_id, src, value, module, state)
           SELECT l.code, 'model', 'ir.actions.client,name', a.id, t.src, t.value, t.module, t.state
             FROM ohada_financial_html_report r
             JOIN ir_act_client a ON (r.name = a.name)
             JOIN ir_translation t ON (t.res_id = r.id AND t.name = 'ohada.financial.html.report,name')
             JOIN res_lang l on  (l.code = t.lang)
            WHERE NOT EXISTS (
                  SELECT 1 FROM ir_translation tt
                  WHERE (tt.name = 'ir.actions.client,name'
                    AND tt.lang = l.code
                    AND type='model'
                    AND tt.res_id = a.id)
                  )
        """)

        # generated missing menu translations for translated reports
        self.env.cr.execute("""
           INSERT INTO ir_translation (lang, type, name, res_id, src, value, module, state)
           SELECT l.code, 'model', 'ir.ui.menu,name', m.id, t.src, t.value, t.module, t.state
             FROM ohada_financial_html_report r
             JOIN ir_ui_menu m ON (r.name = m.name)
             JOIN ir_translation t ON (t.res_id = r.id AND t.name = 'ohada.financial.html.report,name')
             JOIN res_lang l on  (l.code = t.lang)
            WHERE NOT EXISTS (
                  SELECT 1 FROM ir_translation tt
                  WHERE (tt.name = 'ir.ui.menu,name'
                    AND tt.lang = l.code
                    AND type='model'
                    AND tt.res_id = m.id)
                  )
        """)

        return res


class OhadaFinancialReportingDashboard(models.Model):
    _name = "ohada.dashboard"
    _description = "OHADA Dashboard"

    @api.model
    def fetch_data(self, year=None):
        report = self.env['ohada.financial.html.report']
        data = dict()
        if year:
            data['this_year'] = year
            data['prev_year'] = year - 1
        else:
            year = datetime.now().year
            data['this_year'] = datetime.now().year
            data['prev_year'] = datetime.now().year - 1

        options = {'ir_filters': None,
                   'date': {'date_to': str(year) + '-12-31', 'string': str(year), 'filter': 'this_year',
                            'date_from': str(year) + '-01-01'}}

        data['options'] = report.make_temp_options(year)

        data['years'] = [datetime.now().year, datetime.now().year - 1, datetime.now().year - 2, datetime.now().year - 3]
        data['company_name'] = self.env['res.users'].browse(request.session.uid).company_id.name

        bz_id = self.env.ref('ohada_reports.account_financial_report_balancesheet_BZ').id
        dz_id = self.env.ref('ohada_reports.account_financial_report_balancesheet_DZ').id
        xl_id = self.env.ref('ohada_reports.account_financial_report_ohada_profitlost_XI').id
        zh_id = self.env.ref('ohada_reports.account_financial_report_ohada_cashflow_ZH').id

        data['bs_id'] = self.env.ref('ohada_reports.ohada_report_balancesheet_0').id
        data['pl_id'] = self.env.ref('ohada_reports.account_financial_report_ohada_profitlost').id
        data['cf_id'] = self.env.ref('ohada_reports.account_financial_report_ohada_cashflow').id
        # wdb.set_trace()
        # 1st
        data['bz'] = data['bz_d'] = report._get_lines(options, bz_id)[0]['columns'][0]['no_format_name']
        data['dz'] = report._get_lines(options, dz_id)[0]['columns'][0]['no_format_name']
        data['dif_1'] = '$ {:,.2f}'.format(data['bz'] + data['dz'])
        data['bz'] = '$ {:,.2f}'.format(data['bz'])
        data['dz'] = '$ {:,.2f}'.format(data['dz'])

        # 2nd
        data['xl'] = data['xl_d'] = report._get_lines(options, xl_id)[0]['columns'][0]['no_format_name']
        data['xl-1'] = data['xl-1_d'] = report._get_lines({'ir_filters': None,
                                                         'date': {'date_to': str(year - 1) + '-12-31',
                                                                  'string': str(year - 1), 'filter': 'this_year',
                                                                  'date_from': str(year - 1) + '-01-01'}}, xl_id)[0]['columns'][0]['no_format_name']
        data['xl_dif'] = '$ {:,.2f}'.format(data['xl'] - data['xl-1'])
        data['xl'] = '$ {:,.2f}'.format(data['xl'])
        data['xl-1'] = '$ {:,.2f}'.format(data['xl-1'])

        # 3st
        data['zh'] = data['zh_d'] = report._get_lines(options, zh_id)[0]['columns'][0]['no_format_name']
        data['zh-1'] = data['zh-1_d'] = report._get_lines({'ir_filters': None,
                                                         'date': {'date_to': str(year - 1) + '-12-31',
                                                                  'string': str(year - 1), 'filter': 'this_year',
                                                                  'date_from': str(year - 1) + '-01-01'}}, zh_id)[0][
            'columns'][0]['no_format_name']
        data['zh_dif'] = '$ {:,.2f}'.format(data['zh'] - data['zh-1'])
        data['zh'] = '$ {:,.2f}'.format(data['zh'])
        data['zh-1'] = '$ {:,.2f}'.format(data['zh-1'])

        # diagrams
        # [['2016',5], ['2017',1], ['2018',4], ['2019',1]] data for diagrams
        data['di_data'] = {'BS': [], 'PL': [], 'CS': []}

        data['di_data']['BS'] = [[str(year - 3), report._get_lines({'ir_filters': None,
                                                                  'date': {'date_to': str(year - 3) + '-12-31',
                                                                           'string': str(year - 3),
                                                                           'filter': 'this_year',
                                                                           'date_from': str(year - 3) + '-01-01'}},
                                                                 bz_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 2), report._get_lines({'ir_filters': None,
                                                                  'date': {'date_to': str(year - 2) + '-12-31',
                                                                           'string': str(year - 2),
                                                                           'filter': 'this_year',
                                                                           'date_from': str(year - 2) + '-01-01'}},
                                                                 bz_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 1), report._get_lines({'ir_filters': None,
                                                                  'date': {'date_to': str(year - 1) + '-12-31',
                                                                           'string': str(year - 1),
                                                                           'filter': 'this_year',
                                                                           'date_from': str(year - 1) + '-01-01'}},
                                                                 bz_id)[0]['columns'][0]['no_format_name']],
                                 [str(year), data['bz_d']]]

        data['di_data']['PL'] = [[str(year - 3), report._get_lines({'ir_filters': None,
                                                                  'date': {'date_to': str(year - 3) + '-12-31',
                                                                           'string': str(year - 3),
                                                                           'filter': 'this_year',
                                                                           'date_from': str(year - 3) + '-01-01'}},
                                                                 xl_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 2), report._get_lines({'ir_filters': None,
                                                                  'date': {'date_to': str(year - 2) + '-12-31',
                                                                           'string': str(year - 2),
                                                                           'filter': 'this_year',
                                                                           'date_from': str(year - 2) + '-01-01'}},
                                                                 xl_id)[0]['columns'][0]['no_format_name']],
                                 [str(year - 1), data['xl-1_d']],
                                 [str(year), data['xl_d']]]
        # [{count: 1, l_month: "2016"},{count: 5, l_month: "2017"},{count: 4, l_month: "2018"},{count: 6, l_month: "2019"}]}]

        data['di_data']['CS'] = [{'l_month': str(year - 3), 'count': report._get_lines({'ir_filters': None,
                                                                                      'date': {'date_to': str(
                                                                                          year - 3) + '-12-31',
                                                                                               'string': str(year - 3),
                                                                                               'filter': 'this_year',
                                                                                               'date_from': str(
                                                                                                   year - 3) + '-01-01'}},
                                                                                     zh_id)[0]['columns'][0][
            'no_format_name']},
                                 {'l_month': str(year - 2), 'count': report._get_lines({'ir_filters': None,
                                                                                      'date': {'date_to': str(
                                                                                          year - 2) + '-12-31',
                                                                                               'string': str(year - 2),
                                                                                               'filter': 'this_year',
                                                                                               'date_from': str(
                                                                                                   year - 2) + '-01-01'}},
                                                                                     zh_id)[0]['columns'][0][
                                     'no_format_name']},
                                 {'l_month': str(year - 1), 'count': data['zh-1_d']},
                                 {'l_month': str(year), 'count': data['zh_d']}]

        data['menu_id'] = self.env.ref('account_accountant.menu_accounting').id
        data['print_bundle_reports'] = []
        for i in self.env['ohada.financial.html.report'].search([('type', '=', 'main')]):
            data['print_bundle_reports'].append({'name': i.name, 'id': i.id})
        data['print_bundle_reports'].append({'name': 'Notes', 'id': 'notes'})
        data['notes'] = []
        for report in self.env['ohada.financial.html.report'].search([('type', '=', 'note'), ('secondary', '=', False)]):
            data['notes'].append({'name': report.name, 'shortname': report.shortname.upper(), 'id': report.id, 'report_name': report.name})

        data['Cash Flow Statement'] = {'name': 'Tableau des flux de trésorerie',
                                        'id': self.env.ref('ohada_reports.account_financial_report_ohada_cashflow').id}
        data['Profit and lost'] = {'name': 'Profit and Lost',
                                    'id': self.env.ref('ohada_reports.account_financial_report_ohada_profitlost').id}
        data['Balance Sheet'] = {'name': 'Balance Sheet',
                                    'id': self.env.ref('ohada_reports.ohada_report_balancesheet_0').id}

        return data


class OhadaCustomColumns(models.Model):
    _name = "ohada.custom.columns"
    _description = "Table columns with complicated style"

    line_id = fields.Many2one('ohada.financial.html.report.line', 'Financial Report Line')
    cell_id = fields.One2many('ohada.cell.style', 'column_id', default=False)
    line_name = fields.Boolean(default=True)



class OhadaCellStyle(models.Model):
    _name = "ohada.cell.style"
    _description = "Style for cell"

    column_id = fields.Many2one('ohada.custom.columns', 'Table column')

    name = fields.Char()
    colspan = fields.Integer(default=1)
    rowspan = fields.Integer(default=1)
    rotate = fields.Char(default=0)
