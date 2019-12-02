# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import copy
import json
import io
import logging
import lxml.html
import datetime
import ast
import dateparser           #B+

from dateutil.relativedelta import relativedelta


try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, pycompat, config, date_utils
from odoo.osv import expression
from babel.dates import get_quarter_names
from odoo.tools.misc import formatLang, format_date, get_user_companies
from odoo.addons.web.controllers.main import clean_action
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
import wdb

_logger = logging.getLogger(__name__)


class OhadaReportManager(models.Model):
    _name = 'ohada.report.manager'
    _description = 'Manage Summary and Footnotes of OHADA Reports'


    # must work with multi-company, in case of multi company, no company_id defined
    report_name = fields.Char(required=True, help='name of the model of the report')
    summary = fields.Char()
    footnotes_ids = fields.One2many('ohada.report.footnote', 'manager_id')
    company_id = fields.Many2one('res.company')
    financial_report_id = fields.Many2one('ohada.financial.html.report')

    def add_footnote(self, text, line):
        return self.env['ohada.report.footnote'].create({'line': line, 'text': text, 'manager_id': self.id})

class OhadaReportFootnote(models.Model):
    _name = 'ohada.report.footnote'
    _description = 'OHADA Report Footnote'

    text = fields.Char()
    line = fields.Char(index=True)
    manager_id = fields.Many2one('ohada.report.manager')

class OhadaReport(models.AbstractModel):
    _name = 'ohada.report'
    _description = 'OHADA Report'

    MAX_LINES = 80
    filter_multi_company = True
    filter_date = None
    filter_cash_basis = None
    filter_all_entries = None
    filter_comparison = None
    filter_journals = None
    filter_analytic = None
    filter_unfold_all = None
    filter_hierarchy = None
    filter_partner = None

    def has_single_date_filter(self, options):
        '''Determine if we are dealing with options having a single date (options['date']['date']) or
        a date range options['date']['date_from'] -> options['date']['date_to'].

        :param options: The report options.
        :return:        True if False -> date, False otherwise (date_from -> date_to).
        '''
        return options['date'].get('date_from') is None

    def _build_options(self, previous_options=None):
        if not previous_options:
            previous_options = {}
        options = {}
        filter_list = [attr for attr in dir(self) if attr.startswith('filter_') and len(attr) > 7 and not callable(getattr(self, attr))]
        for element in filter_list:
            filter_name = element[7:]
            options[filter_name] = getattr(self, element)

        if options.get('multi_company'):
            company_ids = get_user_companies(self._cr, self.env.user.id)
            if len(company_ids) > 1:
                companies = self.env['res.company'].browse(company_ids)
                options['multi_company'] = [{'id': c.id, 'name': c.name, 'selected': True if c.id == self.env.user.company_id.id else False} for c in companies]
            else:
                del options['multi_company']

        if options.get('journals'):
            options['journals'] = self._get_journals()

        options['unfolded_lines'] = []
        # Merge old options with default from this report
        for key, value in options.items():
            if key in previous_options and value is not None and previous_options[key] is not None:
                # special case handler for date and comparison as from one report to another, they can have either a date range or single date
                if key == 'date' or key == 'comparison':
                    if key == 'comparison':
                        options[key]['number_period'] = previous_options[key]['number_period']
                    options[key]['filter'] = 'custom'
                    if previous_options[key].get('filter', 'custom') != 'custom':
                        # just copy filter and let the system compute the correct date from it
                        options[key]['filter'] = previous_options[key]['filter']
                    elif value.get('date_from') is not None and not previous_options[key].get('date_from'):
                        date = fields.Date.from_string(previous_options[key]['date'])
                        company_fiscalyear_dates = self.env.user.company_id.compute_fiscalyear_dates(date)
                        options[key]['date_from'] = company_fiscalyear_dates['date_from'].strftime(DEFAULT_SERVER_DATE_FORMAT)
                        options[key]['date_to'] = previous_options[key]['date']
                    elif value.get('date') is not None and not previous_options[key].get('date'):
                        options[key]['date'] = previous_options[key]['date_to']
                    else:
                        options[key] = previous_options[key]
                else:
                    options[key] = previous_options[key]
        return options

    @api.model
    def _get_options(self, previous_options=None):
        # Be sure that user has group analytic if a report tries to display analytic
        if self.filter_analytic:
            self.filter_analytic_accounts = [] if self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids else None
            self.filter_analytic_tags = [] if self.env.user.id in self.env.ref('analytic.group_analytic_tags').users.ids else None
            #don't display the analytic filtering options if no option would be shown
            if self.filter_analytic_accounts is None and self.filter_analytic_tags is None:
                self.filter_analytic = None
        if self.filter_partner:
            self.filter_partner_ids = []
            self.filter_partner_categories = []
        return self._build_options(previous_options)

    def get_header(self, options):
        if not options.get('groups', {}).get('ids'):
            return [self._get_columns_name(options)]
        return self._get_columns_name_hierarchy(options)

    #TO BE OVERWRITTEN
    def _get_columns_name_hierarchy(self, options):
        return []

    #TO BE OVERWRITTEN
    def _get_columns_name(self, options):
        return []

    #TO BE OVERWRITTEN
    def _get_lines(self, options, line_id=None):
        return []

    #TO BE OVERWRITTEN
    def _get_templates(self):
        return {
                'main_template': 'ohada_reports.main_template',
                'main_table_header_template': 'ohada_reports.main_table_header',
                'line_template': 'ohada_reports.line_template',
                'footnotes_template': 'ohada_reports.footnotes_template',
                'search_template': 'ohada_reports.search_template',
                'bs_line_template': 'ohada_reports.bs_line_template',
                'bs2_line_template': 'ohada_reports.bs2_line_template',
        }

    #TO BE OVERWRITTEN
    def _get_report_name(self):
        return _('General Report')

    def get_report_filename(self, options):
        """The name that will be used for the file when downloading pdf,xlsx,..."""
        return self._get_report_name().lower().replace(' ', '_')

    def execute_action(self, options, params=None):
        action_id = int(params.get('actionId'))
        action = self.env['ir.actions.actions'].browse([action_id])
        action_type = action.type
        action = self.env[action.type].browse([action_id])
        action_read = action.read()[0]
        if action_type == 'ir.actions.client':
            # Check if we are opening another report and if yes, pass options and ignore_session
            if action.tag == 'ohada_report':
                options['unfolded_lines'] = []
                options['unfold_all'] = False
                another_report_context = safe_eval(action_read['context'])
                another_report = self.browse(another_report_context['id'])
                if not self.date_range and another_report.date_range:
                    # Don't propagate the filter if current report is date based while the targetted
                    # report is date_range based, because the semantic is not the same:
                    # 'End of Following Month' in BS != 'Last Month' in P&L (it has to go from 1st day of fiscalyear)
                    options['date'].pop('filter')
                action_read.update({'options': options, 'ignore_session': 'read'})
        if params.get('id'):
            # Add the id of the ohada.financial.html.report.line in the action's context
            context = action_read.get('context') and safe_eval(action_read['context']) or {}
            context.setdefault('active_id', int(params['id']))
            action_read['context'] = context
        return action_read

    @api.model
    def _resolve_caret_option_document(self, model, res_id, document):
        '''Retrieve the target record of the caret option.

        :param model:       The source model of the report line, 'account.move.line' by default.
        :param res_id:      The source id of the report line.
        :param document:    The target model of the redirection.
        :return: The target record.
        '''
        if model == 'account.invoice':
            if document == 'account.move':
                return self.env[model].browse(res_id).move_id
            if document == 'res.partner':
                return self.env[model].browse(res_id).partner_id.commercial_partner_id
        if model == 'account.invoice.line':
            if document == 'account.move':
                return self.env[model].browse(res_id).invoice_id.move_id
            if document == 'account.invoice':
                return self.env[model].browse(res_id).invoice_id
        if model == 'account.bank.statement.line' and document == 'account.bank.statement':
            return self.env[model].browse(res_id).statement_id

        # model == 'account.move.line' by default.
        if document == 'account.move':
            return self.env[model].browse(res_id).move_id
        if document == 'account.invoice':
            return self.env[model].browse(res_id).invoice_id
        if document == 'account.payment':
            return self.env[model].browse(res_id).payment_id

        return self.env[model].browse(res_id)

    @api.model
    def _resolve_caret_option_view(self, target):
        '''Retrieve the target view name of the caret option.

        :param target:  The target record of the redirection.
        :return: The target view name as a string.
        '''
        if target._name == 'account.invoice':
            if target.type in ('in_refund', 'in_invoice'):
                return 'account.invoice_supplier_form'
            if target.type in ('out_refund', 'out_invoice'):
                return 'account.invoice_form'
        if target._name == 'account.payment':
            return 'account.view_account_payment_form'
        if target._name == 'res.partner':
            return 'base.view_partner_form'
        if target._name == 'account.bank.statement':
            return 'account.view_bank_statement_form'

        # document == 'account.move' by default.
        return 'view_move_form'

    @api.multi
    def open_document(self, options, params=None):
        if not params:
            params = {}

        ctx = self.env.context.copy()
        ctx.pop('id', '')

        # Decode params
        model = params.get('model', 'account.move.line')
        res_id = params.get('id')
        document = params.get('object', 'account.move')

        # Redirection data
        target = self._resolve_caret_option_document(model, res_id, document)
        view_name = self._resolve_caret_option_view(target)
        module = 'account'
        if '.' in view_name:
            module, view_name = view_name.split('.')

        # Redirect
        view_id = self.env['ir.model.data'].get_object_reference(module, view_name)[1]
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': document,
            'view_id': view_id,
            'res_id': target.id,
            'context': ctx,
        }

    def open_action(self, options, domain):
        assert isinstance(domain, (list, tuple))
        domain += [('date', '>=', options.get('date').get('date_from')),
                   ('date', '<=', options.get('date').get('date_to'))]
        if not options.get('all_entries'):
            domain += [('move_id.state', '=', 'posted')]

        ctx = self.env.context.copy()
        ctx.update({'search_default_account': 1, 'search_default_groupby_date': 1})

        action = self.env.ref('account.action_move_line_select_tax_audit').read()[0]
        action = clean_action(action)
        action['domain'] = domain
        action['context'] = ctx
        return action

    def open_tax(self, options, params=None):
        active_id = int(str(params.get('id')).split('_')[0])
        tax = self.env['account.tax'].browse(active_id)
        domain = ['|', ('tax_ids', 'in', [active_id]),
                       ('tax_line_id', 'in', [active_id])]
        if tax.tax_exigibility == 'on_payment':
            domain += [('tax_exigible', '=', True)]
        return self.open_action(options, domain)

    def open_tax_report_line(self, options, params=None):
        active_id = int(str(params.get('id')).split('_')[0])
        line = self.env['ohada.financial.html.report.line'].browse(active_id)
        domain = ast.literal_eval(line.domain)
        action = self.open_action(options, domain)
        action['display_name'] = _('Journal Items (%s)') % line.name
        return action

    def view_too_many(self, options, params=None):
        model, active_id = params.get('actionId').split(',')
        ctx = self.env.context.copy()
        if model == 'account':
            action = self.env.ref('account.action_move_line_select').read()[0]
            ctx.update({
                'search_default_account_id': [int(active_id)],
                'active_id': int(active_id),
                })
        if model == 'partner':
            action = self.env.ref('account.action_move_line_select_by_partner').read()[0]
            ctx.update({
                'search_default_partner_id': [int(active_id)],
                'active_id': int(active_id),
                })
        action = clean_action(action)
        action['context'] = ctx
        return action

    @api.multi
    def open_general_ledger(self, options, params=None):
        if not params:
            params = {}
        ctx = self.env.context.copy()
        ctx.pop('id', '')
        action = self.env.ref('account_reports.action_account_report_general_ledger').read()[0]
        options['unfolded_lines'] = ['account_%s' % (params.get('id', ''),)]
        options['unfold_all'] = False
        ctx.update({'model': 'account.general.ledger'})
        action.update({'options': options, 'context': ctx, 'ignore_session': 'read'})
        return action

    def open_unposted_moves(self, options, params=None):
        ''' Open the list of draft journal entries that might impact the reporting'''
        action = self.env.ref('account.action_move_journal_line').read()[0]
        action = clean_action(action)
        domain = [('state', '=', 'draft')]
        if options.get('date'):
            #there's no condition on the date from, as a draft entry might change the initial balance of a line
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            domain += [('date', '<=', date_to)]
        action['domain'] = domain
        #overwrite the context to avoid default filtering on 'misc' journals
        action['context'] = {}
        return action

    def open_journal_items(self, options, params):
        action = self.env.ref('account.action_move_line_select').read()[0]
        action = clean_action(action)
        ctx = self.env.context.copy()
        if params and 'id' in params:
            active_id = params['id']
            ctx.update({
                    'search_default_account_id': [active_id],
            })

        if options:
            if options.get('journals'):
                selected_journals = [journal['id'] for journal in options['journals'] if journal.get('selected')]
                if selected_journals: # Otherwise, nothing is selected, so we want to display everything
                    ctx.update({
                        'search_default_journal_id': selected_journals,
                    })

            domain = expression.normalize_domain(ast.literal_eval(action.get('domain', '[]')))
            if options.get('analytic_accounts'):
                analytic_ids = [int(r) for r in options['analytic_accounts']]
                domain = expression.AND([domain, [('analytic_account_id', 'in', analytic_ids)]])
            if options.get('date'):
                opt_date = options['date']
                if opt_date.get('date_from'):
                    domain = expression.AND([domain, [('date', '>=', opt_date['date_from'])]])
                if opt_date.get('date_to'):
                    domain = expression.AND([domain, [('date', '<=', opt_date['date_to'])]])
            # In case the line has been generated for a "group by" financial line, append the parent line's domain to the one we created
            if params.get('financial_group_line_id'):
                parent_financial_report_line = self.env['ohada.financial.html.report.line'].browse(params['financial_group_line_id'])
                domain = expression.AND([domain, safe_eval(parent_financial_report_line.domain)])

            if not options.get('all_entries'):
                ctx['search_default_posted'] = True

            action['domain'] = domain
        action['context'] = ctx
        return action

    def reverse(self, values):
        """Utility method used to reverse a list, this method is used during template generation in order to reverse periods for example"""
        if type(values) != list:
            return values
        else:
            inv_values = copy.deepcopy(values)
            inv_values.reverse()
        return inv_values

    def _set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        ctx = self.env.context.copy()
        if options.get('cash_basis'):
            ctx['cash_basis'] = True
        if options.get('date') and options['date'].get('date_from'):
            ctx['date_from'] = options['date']['date_from']
        if options.get('date'):
            ctx['date_to'] = options['date'].get('date_to') or options['date'].get('date')
        if options.get('all_entries') is not None:
            ctx['state'] = options.get('all_entries') and 'all' or 'posted'
        if options.get('journals'):
            ctx['journal_ids'] = [j.get('id') for j in options.get('journals') if j.get('selected')]
        company_ids = []
        if options.get('multi_company'):
            company_ids = [c.get('id') for c in options['multi_company'] if c.get('selected')]
            company_ids = company_ids if len(company_ids) > 0 else [c.get('id') for c in options['multi_company']]
        ctx['company_ids'] = len(company_ids) > 0 and company_ids or [self.env.user.company_id.id]
        if options.get('analytic_accounts'):
            ctx['analytic_account_ids'] = self.env['account.analytic.account'].browse([int(acc) for acc in options['analytic_accounts']])
        if options.get('analytic_tags'):
            ctx['analytic_tag_ids'] = self.env['account.analytic.tag'].browse([int(t) for t in options['analytic_tags']])
        if options.get('partner_ids'):
            ctx['partner_ids'] = self.env['res.partner'].browse([int(partner) for partner in options['partner_ids']])
        if options.get('partner_categories'):
            ctx['partner_categories'] = self.env['res.partner.category'].browse([int(category) for category in options['partner_categories']])
        return ctx

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self._get_options(options)
        # apply date and date_comparison filter
        self._apply_date_filter(options)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic_accounts') is not None:
            searchview_dict['analytic_accounts'] = self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids and [(t.id, t.name) for t in self.env['account.analytic.account'].search([])] or False
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
        if options.get('analytic_tags') is not None:
            searchview_dict['analytic_tags'] = self.env.user.id in self.env.ref('analytic.group_analytic_tags').users.ids and [(t.id, t.name) for t in self.env['account.analytic.tag'].search([])] or False
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in options['partner_categories']]

        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))

        report_manager = self._get_report_manager(options)
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view'].render_template(self._get_templates().get('search_template', 'ohada_report.search_template'), values=searchview_dict),
                }
        return info

    @api.model
    def _create_hierarchy(self, lines):
        """This method is called when the option 'hiearchy' is enabled on a report.
        It receives the lines (as computed by _get_lines()) in argument, and will add
        a hiearchy in those lines by using the account.group of accounts. If not set,
        it will fallback on creating a hierarchy based on the account's code first 3
        digits.
        """
        # Avoid redundant browsing.
        accounts_cache = {}

        MOST_SORT_PRIO = 0
        LEAST_SORT_PRIO = 99

        # Retrieve account either from cache, either by browsing.
        def get_account(id):
            if id not in accounts_cache:
                accounts_cache[id] = self.env['account.account'].browse(id)
            return accounts_cache[id]

        # Create codes path in the hierarchy based on account.
        def get_account_codes(account):
            # A code is tuple(sort priority, actual code)
            codes = []
            if account.group_id:
                group = account.group_id
                while group:
                    code = '%s %s' % (group.code_prefix or '', group.name)
                    codes.append((MOST_SORT_PRIO, code))
                    group = group.parent_id
            else:
                # Limit to 3 levels.
                code = account.code[:3]
                while code:
                    codes.append((MOST_SORT_PRIO, code))
                    code = code[:-1]
            return list(reversed(codes))

        # Add the report line to the hierarchy recursively.
        def add_line_to_hierarchy(line, codes, level_dict, depth=None):
            # Recursively build a dict where:
            # 'children' contains only subcodes
            # 'lines' contains the lines at this level
            # This > lines [optional, i.e. not for topmost level]
            #      > children > [codes] "That" > lines
            #                                  > metadata
            #                                  > children
            #      > metadata(depth, parent ...)

            if not codes:
                return
            if not depth:
                depth = line.get('level', 1)
            level_dict.setdefault('depth', depth)
            level_dict.setdefault('parent_id', line.get('parent_id'))
            level_dict.setdefault('children', {})
            code = codes[0]
            codes = codes[1:]
            level_dict['children'].setdefault(code, {})

            if codes:
                add_line_to_hierarchy(line, codes, level_dict['children'][code], depth=depth + 1)
            else:
                level_dict['children'][code].setdefault('lines', [])
                level_dict['children'][code]['lines'].append(line)

        # Merge a list of columns together and take care about str values.
        def merge_columns(columns):
            return ['n/a' if any(isinstance(i, str) for i in x) else sum(x) for x in pycompat.izip(*columns)]

        # Get_lines for the newly computed hierarchy.
        def get_hierarchy_lines(values, depth=1):
            lines = []
            sum_sum_columns = []
            for base_line in values.get('lines', []):
                lines.append(base_line)
                sum_sum_columns.append([c.get('no_format_name', c['name']) for c in base_line['columns']])

            # For the last iteration, there might not be the children key (see add_line_to_hierarchy)
            for key in sorted(values.get('children', {}).keys()):
                sum_columns, sub_lines = get_hierarchy_lines(values['children'][key], depth=values['depth'])
                header_line = {
                    'id': 'hierarchy',
                    'name': key[1],  # second member of the tuple
                    'unfoldable': False,
                    'unfolded': True,
                    'level': values['depth'],
                    'parent_id': values['parent_id'],
                    'columns': [{'name': self.format_value(c) if not isinstance(c, str) else c} for c in sum_columns],
                }
                if key[0] == LEAST_SORT_PRIO:
                    header_line['style'] = 'font-style:italic;'
                lines += [header_line] + sub_lines
                sum_sum_columns.append(sum_columns)
            return merge_columns(sum_sum_columns), lines

        def deep_merge_dict(source, destination):
            for key, value in source.items():
                if isinstance(value, dict):
                    # get node or create one
                    node = destination.setdefault(key, {})
                    deep_merge_dict(value, node)
                else:
                    destination[key] = value

            return destination

        # Hierarchy of codes.
        accounts_hierarchy = {}

        new_lines = []
        no_group_lines = []
        # If no account.group at all, we need to pass once again in the loop to dispatch
        # all the lines across their account prefix, hence the None
        for line in lines + [None]:
            # Only deal with lines grouped by accounts.
            # And discriminating sections defined by ohada.financial.html.report.line
            is_grouped_by_account = line and line.get('caret_options') == 'account.account'
            if not is_grouped_by_account or not line:

                # No group code found in any lines, compute it automatically.
                no_group_hierarchy = {}
                for no_group_line in no_group_lines:
                    codes = [(LEAST_SORT_PRIO, _('(No Group)'))]
                    if not accounts_hierarchy:
                        account = get_account(no_group_line.get('id'))
                        codes = get_account_codes(account)
                    add_line_to_hierarchy(no_group_line, codes, no_group_hierarchy)
                no_group_lines = []

                deep_merge_dict(no_group_hierarchy, accounts_hierarchy)

                # Merge the newly created hierarchy with existing lines.
                if accounts_hierarchy:
                    new_lines += get_hierarchy_lines(accounts_hierarchy)[1]
                    accounts_hierarchy = {}

                if line:
                    new_lines.append(line)
                continue

            # Exclude lines having no group.
            account = get_account(line.get('id'))
            if not account.group_id:
                no_group_lines.append(line)
                continue

            codes = get_account_codes(account)
            add_line_to_hierarchy(line, codes, accounts_hierarchy)

        return new_lines

    @api.multi
    def _check_report_security(self, options):
        '''The security check must be done in this method. It ensures no-one can by-passing some access rules
        (e.g. falsifying the options).

        :param options:     The report options.
        '''
        # Check the options has not been falsified in order to access not allowed companies.
        user_company_ids = self.env.user.company_ids.ids
        if options.get('multi_company'):
            group_multi_company = self.env.ref('base.group_multi_company')
            if self.env.user.id not in group_multi_company.users.ids:
                options.pop('multi_company')
            else:
                for c in options['multi_company']:
                    if c['selected'] and c['id'] not in user_company_ids:
                        c['selected'] = False

    @api.multi
    def get_html(self, options, line_id=None, additional_context=None):
        '''
        return the html value of report, or html value of unfolded line
        * if line_id is set, the template used will be the line_template
        otherwise it uses the main_template. Reason is for efficiency, when unfolding a line in the report
        we don't want to reload all lines, just get the one we unfolded.
        '''
        # Check the security before updating the context to make sure the options are safe.
        if self.name == 'Balance Sheet':
            return self.get_html_bs(options, line_id, additional_context)
        self._check_report_security(options)

        # Prevent inconsistency between options and context.
        self = self.with_context(self._set_context(options))

        # wdb.set_trace()
        templates = self._get_templates()
        report_manager = self._get_report_manager(options)
        date = options['date'].get('date_from') or options['date'].get('date')
        report = {'name': self._get_report_name(),
                  'summary': report_manager.summary,
                  'company_name': self.env.user.company_id.name,
                  'type': self.type,
                  'vat': self.env.user.company_id.vat,
                  'year': date[0:4],
                  'header': self.header and self.header + ' ' + date[0:4],}
        lines = self._get_lines(options, line_id=line_id)

        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines)

        footnotes_to_render = []
        # if self.env.context.get('print_mode', False):
        #     # we are in print mode, so compute footnote number and include them in lines values, otherwise, let the js compute the number correctly as
        #     # we don't know all the visible lines.
        #     footnotes = dict([(str(f.line), f) for f in report_manager.footnotes_ids])
        #     number = 0
        #     for line in lines:
        #         f = footnotes.get(str(line.get('id')))
        #         if f:
        #             number += 1
        #             line['footnote'] = str(number)
        #             footnotes_to_render.append({'id': f.id, 'number': number, 'text': f.text})

        rcontext = {'report': report,
                    'lines': {'columns_header': self.get_header(options), 'lines': lines},
                    'options': options,
                    'context': self.env.context,
                    'model': self,
                }
        if additional_context and type(additional_context) == dict:
            rcontext.update(additional_context)
        if self.env.context.get('analytic_account_ids'):
            rcontext['options']['analytic_account_ids'] = [
                {'id': acc.id, 'name': acc.name} for acc in self.env.context['analytic_account_ids']
            ]

        render_template = templates.get('main_template', 'ohada_reports.main_template')
        if line_id is not None:
            render_template = templates.get('line_template', 'ohada_reports.line_template')
        html = self.env['ir.ui.view'].render_template(
            render_template,
            values=dict(rcontext),
        )
        # if self.env.context.get('print_mode', False):
        #     for k,v in self._replace_class().items():
        #         html = html.replace(k, v)
        #     # append footnote as well
        #     html = html.replace(b'<div class="js_account_report_footnotes"></div>', self.get_html_footnotes(footnotes_to_render))
        return html

    @api.multi
    def get_html_footnotes(self, footnotes):
        template = self._get_templates().get('footnotes_template', 'ohada_reports.footnotes_template')
        rcontext = {'footnotes': footnotes, 'context': self.env.context}
        html = self.env['ir.ui.view'].render_template(template, values=dict(rcontext))
        return html

    def _get_reports_buttons(self):
        return [{'name': _('Print Preview'), 'action': 'print_pdf'}, {'name': _('Export (XLSX)'), 'action': 'print_xlsx'}]

    def _get_report_manager(self, options):
        domain = [('report_name', '=', self._name)]
        domain = (domain + [('financial_report_id', '=', self.id)]) if 'id' in dir(self) else domain
        selected_companies = []
        if options.get('multi_company'):
            selected_companies = [c['id'] for c in options['multi_company'] if c.get('selected')]
        if len(selected_companies) == 1:
            domain += [('company_id', '=', selected_companies[0])]
        existing_manager = self.env['ohada.report.manager'].search(domain, limit=1)
        if not existing_manager:
            existing_manager = self.env['ohada.report.manager'].create({'report_name': self._name, 'company_id': selected_companies and selected_companies[0] or False, 'financial_report_id': self.id if 'id' in dir(self) else False})
        return existing_manager

    def _get_filter_journals(self):
        return self.env['account.journal'].search([('company_id', 'in', self.env.user.company_ids.ids or [self.env.user.company_id.id])], order="company_id, name")

    def _get_journals(self):
        journals_read = self._get_filter_journals()
        journals = []
        previous_company = False
        for c in journals_read:
            if c.company_id != previous_company:
                journals.append({'id': 'divider', 'name': c.company_id.name})
                previous_company = c.company_id
            journals.append({'id': c.id, 'name': c.name, 'code': c.code, 'type': c.type, 'selected': False})
        return journals

    def _get_dates_period(self, options, date_from, date_to, period_type=None):
        '''Compute some information about the period:
        * The name to display on the report.
        * The period type (e.g. quarter) if not specified explicitly.

        :param options:     The report options.
        :param date_from:   The starting date of the period.
        :param date_to:     The ending date of the period.
        :param period_type: The type of the interval date_from -> date_to.
        :return:            A dictionary containing:
            * date_from * date_to * string * period_type *
        '''
        def match(dt_from, dt_to):
            if self.has_single_date_filter(options):
                return (date_to or date_from) == dt_to
            else:
                return (dt_from, dt_to) == (date_from, date_to)

        string = None
        # If no date_from or not date_to, we are unable to determine a period
        if not period_type:
            date = date_to or date_from
            company_fiscalyear_dates = self.env.user.company_id.compute_fiscalyear_dates(date)
            if match(company_fiscalyear_dates['date_from'], company_fiscalyear_dates['date_to']):
                period_type = 'fiscalyear'
                if company_fiscalyear_dates.get('record'):
                    string = company_fiscalyear_dates['record'].name
            elif match(*date_utils.get_month(date)):
                period_type = 'month'
            elif match(*date_utils.get_quarter(date)):
                period_type = 'quarter'
            elif match(*date_utils.get_fiscal_year(date)):
                period_type = 'year'
            else:
                period_type = 'custom'

        if not string:
            fy_day = self.env.user.company_id.fiscalyear_last_day
            fy_month = self.env.user.company_id.fiscalyear_last_month
            if self.has_single_date_filter(options):
                string = _('As of %s') % (format_date(self.env, date_to.strftime(DEFAULT_SERVER_DATE_FORMAT)))
            elif period_type == 'year' or (period_type == 'fiscalyear' and (date_from, date_to) == date_utils.get_fiscal_year(date_to)):
                string = date_to.strftime('%Y')
            elif period_type == 'fiscalyear' and (date_from, date_to) == date_utils.get_fiscal_year(date_to, day=fy_day, month=fy_month):
                string = '%s - %s' % (date_to.year - 1, date_to.year)
            elif period_type == 'month':
                string = format_date(self.env, date_to.strftime(DEFAULT_SERVER_DATE_FORMAT), date_format='MMM YYYY')
            elif period_type == 'quarter':
                quarter_names = get_quarter_names('abbreviated', locale=self.env.context.get('lang') or 'en_US')
                string = u'%s\N{NO-BREAK SPACE}%s' % (quarter_names[date_utils.get_quarter_number(date_to)], date_to.year)
            else:
                dt_from_str = format_date(self.env, date_from.strftime(DEFAULT_SERVER_DATE_FORMAT))
                dt_to_str = format_date(self.env, date_to.strftime(DEFAULT_SERVER_DATE_FORMAT))
                string = _('From %s \n to  %s') % (dt_from_str, dt_to_str)

        return {
            'string': string,
            'period_type': period_type,
            'date_from': date_from,
            'date_to': date_to,
        }

    def _get_dates_previous_period(self, options, period_vals):
        '''Shift the period to the previous one.

        :param options:     The report options.
        :param period_vals: A dictionary generated by the _get_dates_period method.
        :return:            A dictionary containing:
            * date_from * date_to * string * period_type *
        '''
        period_type = period_vals['period_type']
        date_from = period_vals['date_from']
        date_to = period_vals['date_to']

        if not date_from or not date_to:
            date = (date_from or date_to).replace(day=1) - datetime.timedelta(days=1)
            # Propagate the period_type to avoid bad behavior.
            # E.g. custom single date 2018-01-30 with previous period will produce 2017-12-31 that
            # must not be interpreted as a fiscal year.
            return self._get_dates_period(options, None, date, period_type=period_type)

        date_to = date_from - datetime.timedelta(days=1)
        if period_type == 'fiscalyear':
            # Don't pass the period_type to _get_dates_period to be able to retrieve the account.fiscal.year record if
            # necessary.
            company_fiscalyear_dates = self.env.user.company_id.compute_fiscalyear_dates(date_to)
            return self._get_dates_period(options, company_fiscalyear_dates['date_from'], company_fiscalyear_dates['date_to'])
        if period_type == 'month':
            return self._get_dates_period(options, *date_utils.get_month(date_to), period_type='month')
        if period_type == 'quarter':
            return self._get_dates_period(options, *date_utils.get_quarter(date_to), period_type='quarter')
        if period_type == 'year':
            return self._get_dates_period(options, *date_utils.get_fiscal_year(date_to), period_type='year')
        date_from = date_to - datetime.timedelta(days=(period_vals['date_to'] - date_from).days)
        return self._get_dates_period(options, date_from, date_to)

    def _get_dates_previous_year(self, options, period_vals):
        '''Shift the period to the previous year.

        :param options:     The report options.
        :param period_vals: A dictionary generated by the _get_dates_period method.
        :return:            A dictionary containing:
            * date_from * date_to * string * period_type *
        '''
        period_type = period_vals['period_type']
        date_from = period_vals['date_from']
        date_to = period_vals['date_to']

        # Note: Use relativedelta to avoid moving from 2016-02-29 -> 2015-02-29 and then, have a day out of range.
        if not date_from or not date_to:
            date_to = date_from or date_to
            date_from = None

        date_to = date_to - relativedelta(years=1)
        # Take care about the 29th february.
        # Moving from 2017-02-28 -> 2016-02-28 is wrong! It must be 2016-02-29.
        if period_type == 'month':
            date_from, date_to = date_utils.get_month(date_to)
        elif date_from:
            date_from = date_from - relativedelta(years=1)
        return self._get_dates_period(options, date_from, date_to, period_type=period_type)

    def format_value(self, value, currency=False):
        ''' #E+
            in OHADA reports, the currency is not displayed, all amounts must be reported in XOF which is the company currency
            By default, we consider that all values are in the company currency. 
            TODO: 
                Below, we display the currency only if it's another one. 
                But we will have to convert amounts in different currencies to convert the compnay currency (XOF)
        '''
        currency_id = currency or self.env.user.company_id.currency_id
        if self.env.context.get('no_format'):
            return currency_id.round(value)
        if currency_id.is_zero(value):
            # don't print -0.0 in reports
            value = abs(value)
        #res = formatLang(self.env, value, currency_obj=currency_id)   #E- replaced by next if/else-block
        if currency and currency != report_currency_id:
            #TODO: Here we need to convert the value to the company currency
            res = formatLang(self.env, value, currency_obj=report_currency_id)
        else:   
            res = formatLang(self.env, value, currency_obj=currency_id)     #formatLang(self.env, value, digits=0)
        return res

    def _format_aml_name(self, aml):
        name = '-'.join(
            (aml.move_id.name not in ['', '/'] and [aml.move_id.name] or []) +
            (aml.ref not in ['', '/', False] and [aml.ref] or []) +
            ([aml.name] if aml.name and aml.name not in ['', '/'] else [])
        )
        if len(name) > 35 and not self.env.context.get('no_format'):
            name = name[:32] + "..."
        return name

    def format_date(self, options, dt_filter='date'):
        # previously get_full_date_names
        if self.has_single_date_filter(options):
            dt_from = None
            dt_to = fields.Date.from_string(options[dt_filter]['date'])
            if not dt_to:
                raise UserError(_('Please specify an end date.'))
        else:
            dt_from = fields.Date.from_string(options[dt_filter]['date_from'])
            dt_to = fields.Date.from_string(options[dt_filter]['date_to'])
            if not dt_from or not dt_to:
                raise UserError(_('Please specify a start and end date.'))

        return self._get_dates_period(options, dt_from, dt_to)['string']

    def _apply_date_filter(self, options):
        def create_vals(period_vals):
            vals = {'string': period_vals['string']}
            if self.has_single_date_filter(options):
                vals['date'] = (period_vals['date_to'] or period_vals['date_from']).strftime(DEFAULT_SERVER_DATE_FORMAT)
            else:
                vals['date_from'] = period_vals['date_from'].strftime(DEFAULT_SERVER_DATE_FORMAT)
                vals['date_to'] = period_vals['date_to'].strftime(DEFAULT_SERVER_DATE_FORMAT)
            return vals
        # ===== Date Filter =====
        if not options.get('date') or not options['date'].get('filter'):
            return
        options_filter = options['date']['filter']

        date_from = None
        date_to = fields.Date.context_today(self)
        period_type = None
        if options_filter == 'custom':
            if self.has_single_date_filter(options):
                date_from = None
                date_to = fields.Date.from_string(options['date']['date'])
            else:
                date_from = fields.Date.from_string(options['date']['date_from'])
                date_to = fields.Date.from_string(options['date']['date_to'])
        elif 'today' in options_filter:
            if not self.has_single_date_filter(options):
                date_from = self.env.user.company_id.compute_fiscalyear_dates(date_to)['date_from']
        elif 'month' in options_filter:
            period_type = 'month'
            date_from, date_to = date_utils.get_month(date_to)
        elif 'quarter' in options_filter:
            period_type = 'quarter'
            date_from, date_to = date_utils.get_quarter(date_to)
        elif 'year' in options_filter:
            company_fiscalyear_dates = self.env.user.company_id.compute_fiscalyear_dates(date_to)
            date_from = company_fiscalyear_dates['date_from']
            date_to = company_fiscalyear_dates['date_to']
        else:
            raise UserError('Programmation Error: Unrecognized parameter %s in date filter!' % str(options_filter))

        period_vals = self._get_dates_period(options, date_from, date_to, period_type)
        if 'last' in options_filter:
            period_vals = self._get_dates_previous_period(options, period_vals)

        options['date'].update(create_vals(period_vals))

        # ===== Comparison Filter =====
        if not options.get('comparison') or not options['comparison'].get('filter'):
            return
        cmp_filter = options['comparison']['filter']
        if cmp_filter == 'no_comparison':
            if self.name == 'Balance Sheet - Assets':
                periods = []
                number_period = 1
                for index in range(0, number_period):
                    if cmp_filter == 'previous_period':
                        period_vals = self._get_dates_previous_period(options, period_vals)
                    else:
                        period_vals = self._get_dates_previous_year(options, period_vals)
                    periods.append(create_vals(period_vals))

                if len(periods) > 0:
                    options['comparison'].update(periods[-1])
                options['comparison']['periods'] = periods
                options['comparison']['filter'] = 'no_comparison'
                options['comparison']['string'] = _('No comparison')
                return
            if self.type == 'note':
                periods = []
                number_period = 1
                for index in range(0, number_period):
                    if cmp_filter == 'previous_period':
                        period_vals = self._get_dates_previous_period(options, period_vals)
                    else:
                        period_vals = self._get_dates_previous_year(options, period_vals)
                    periods.append(create_vals(period_vals))

                if len(periods) > 0:
                    options['comparison'].update(periods[-1])
                options['comparison']['periods'] = periods
                options['comparison']['filter'] = 'previous_period'
                options['comparison']['string'] = _('No comparison')
                return

            periods = []
            number_period = 1
            for index in range(0, number_period):
                period_vals = self._get_dates_previous_period(options, period_vals)
                periods.append(create_vals(period_vals))

            if len(periods) > 0:
                options['comparison'].update(periods[0])
            options['comparison']['periods'] = periods
            options['comparison']['string'] = _('No comparison')
            return

        if cmp_filter == 'custom':
            if self.has_single_date_filter(options):
                date_from = None
                date_to = fields.Date.from_string(options['comparison']['date'])
            else:
                date_from = fields.Date.from_string(options['comparison']['date_from'])
                date_to = fields.Date.from_string(options['comparison']['date_to'])
            vals = create_vals(self._get_dates_period(options, date_from, date_to))
            options['comparison']['periods'] = [vals]
            return
        periods = []
        number_period = options['comparison'].get('number_period', 1) or 0
        for index in range(0, number_period):
            if cmp_filter == 'previous_period':
                period_vals = self._get_dates_previous_period(options, period_vals)
            else:
                period_vals = self._get_dates_previous_year(options, period_vals)
            periods.append(create_vals(period_vals))

        if len(periods) > 0:
            options['comparison'].update(periods[-1])
        options['comparison']['periods'] = periods

    def print_pdf(self, options):
        return {
                'type': 'ir_actions_account_report_download',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'pdf',
                         'financial_id': self.env.context.get('id'),
                         }
                }

    def _replace_class(self):
        """When printing pdf, we sometime want to remove/add/replace class for the report to look a bit different on paper
        this method is used for this, it will replace occurence of value key by the dict value in the generated pdf
        """
        return {b'o_account_reports_no_print': b'', b'table-responsive': b'', b'<a': b'<span', b'</a>': b'</span>'}

    def get_pdf(self, options, minimal_layout=True, horizontal=False):
        # As the assets are generated during the same transaction as the rendering of the
        # templates calling them, there is a scenario where the assets are unreachable: when
        # you make a request to read the assets while the transaction creating them is not done.
        # Indeed, when you make an asset request, the controller has to read the `ir.attachment`
        # table.
        # This scenario happens when you want to print a PDF report for the first time, as the
        # assets are not in cache and must be generated. To workaround this issue, we manually
        # commit the writes in the `ir.attachment` table. It is done thanks to a key in the context.


        # wdb.set_trace()
        if not config['test_enable']:
            self = self.with_context(commit_assetsbundle=True)

        # base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url = 'http://127.0.0.1:8069'

        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.user.company_id,
        }

        body = self.env['ir.ui.view'].render_template(
            "ohada_reports.print_template",
            values=dict(rcontext),
        )
        if self.name == 'Balance Sheet' and horizontal is False:
            body_html = b''
            body_html += self.env.ref('ohada_reports.account_financial_report_ohada_balancesheet').get_html(options)
            body_html += self.env.ref('ohada_reports.account_financial_report_ohada_balancesheet_liabilitites0').get_html(options)
        else:
            body_html = self.get_html(options)
        # wdb.set_trace()
        body = body.replace(b'<body class="o_account_reports_body_print">', b'<body class="o_account_reports_body_print">' + body_html)

        if self.name == 'Balance Sheet' and horizontal is True:
            body = body.replace(b'<div class="container o_account_reports_page o_account_reports_no_print page" style="padding-top:0px;padding-bottom:0px;">', b'<div class="o_account_reports_page o_account_reports_no_print page" style="padding-top:0px;padding-bottom:0px;">')
            body = body.replace(b'<table style="margin-top:10px;margin-bottom:10px;color:#001E5A;font-weight:normal;float:left;"', b'<table style="font-size:8px !important;width:30%;margin-bottom:10px;color:#001E5A;font-weight:normal;float:left;"')
            body = body.replace(b'<table style="margin-bottom:10px;color:#001E5A;font-weight:normal;float:left;"', b'<table style="margint-left:-9px;font-size:8px !important;width:30%;margin-bottom:10px;color:#001E5A;font-weight:normal;float:left;"')

        if minimal_layout:
            header = ''
            footer = self.env['ir.actions.report'].render_template("ohada_reports.internal_layout_ohada", values=rcontext)
            spec_paperformat_args = {'data-report-margin-top': 10, 'data-report-header-spacing': 10}
            footer = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=footer))
        else:
            rcontext.update({
                    'css': '',
                    'o': self.env.user,
                    'res_company': self.env.user.company_id,
                })
            header = self.env['ir.actions.report'].render_template("web.external_layout", values=rcontext)
            header = header.decode('utf-8') # Ensure that headers and footer are correctly encoded
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
                    headers = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=headers))

                for node in root.xpath(match_klass.format('footer')):
                    footer = lxml.html.tostring(node)
                    footer = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=footer))

            except lxml.etree.XMLSyntaxError:
                headers = header.encode()
                footer = b''
            header = headers

        landscape = horizontal
        if len(self.with_context(print_mode=True).get_header(options)[-1]) > 5:
            landscape = True

        return self.env['ir.actions.report']._run_wkhtmltopdf(
            [body],
            header=header, footer=footer,
            landscape=landscape,
            specific_paperformat_args=spec_paperformat_args
        )

    def print_xlsx(self, options):
        return {
                'type': 'ir_actions_account_report_download',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'xlsx',
                         'financial_id': self.env.context.get('id'),
                         }
                }

    def _get_super_columns(self, options):
        """
        Essentially used when getting the xlsx of a report
        Some reports may need super title cells on top of regular
        columns title, This methods retrieve the formers.
        e.g. in Trial Balance, you can compare periods (super cells)
            and each have debit/credit columns


        @params {dict} options: options for computing the report
        @return {dict}:
            {list(dict)} columns: the dict of the super columns of the xlsx report,
                the columns' string is contained into the 'string' key
            {int} merge: optional parameter. Indicates to xlsxwriter
                that it should put the contents of each column into the resulting
                cell of the merge of this [merge] number of cells
                -- only merging on one line is supported
            {int} x_offset: tells xlsxwriter it should start writing the columns from
                [x_offset] cells on the left
        """
        return {}

    def get_xlsx(self, options, response, print_bundle=False, workbook=None):
        output = io.BytesIO()
        if print_bundle == False:
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self._get_report_name()[:31])


        top_border = workbook.add_format({'bottom': 6, 'border_color': '#001E5A'})
        bottom_border = workbook.add_format({'top': 6, 'border_color': '#001E5A'})
        right_border = workbook.add_format({'left': 6, 'border_color': '#001E5A'})
        left_border = workbook.add_format({'right': 6, 'border_color': '#001E5A'})
        date_default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#001E5A', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format({'font_name': 'NimbusSanL', 'font_size': 12, 'font_color': '#001E5A', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format({'font_name': 'NimbusSanL', 'font_size': 12, 'font_color': '#001E5A', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'NimbusSanL', 'font_size': 12, 'font_color': '#001E5A'})
        title_style = workbook.add_format({'font_name': 'NimbusSanL', 'bold': True, 'bottom': 2})
        super_col_style = workbook.add_format({'font_name': 'NimbusSanL', 'bold': True, 'align': 'center'})
        level_0_style = workbook.add_format({'valign': 'vcenter', 'border_color': '#001E5A', 'shrink': True, 'align': 'center', 'bg_color': '#CDEBFF', 'font_name': 'NimbusSanL', 'bold': True, 'font_size': 8, 'border': 1, 'font_color': '#001E5A'})
        level_1_style = workbook.add_format({'valign': 'vcenter', 'border_color': '#001E5A', 'border': 1, 'align': 'center', 'bold': True, 'bg_color':'#FFDCDC','font_name': 'NimbusSanL', 'font_size': 8, 'bottom': 1, 'font_color': '#001E5A'})
        level_2_col1_style = workbook.add_format({'border_color': '#001E5A', 'border': 1, 'font_name': 'NimbusSanL', 'font_size': 8, 'font_color': '#001E5A', 'indent': 1})
        level_2_col1_total_style = workbook.add_format({'border_color': '#001E5A', 'border': 1, 'font_name': 'NimbusSanL', 'font_size': 8, 'font_color': '#001E5A'})
        level_2_style = workbook.add_format({'border_color': '#001E5A', 'border': 1, 'font_name': 'NimbusSanL', 'font_size': 8, 'font_color': '#001E5A'})
        level_3_col1_style = workbook.add_format({'border_color': '#001E5A', 'border': 1, 'font_name': 'NimbusSanL', 'font_size': 8, 'font_color': '#001E5A', 'indent': 2})
        level_3_col1_total_style = workbook.add_format({'border_color': '#001E5A', 'border': 1, 'font_name': 'NimbusSanL', 'font_size': 8, 'font_color': '#001E5A', 'indent': 1})
        level_3_style = workbook.add_format({'border_color': '#001E5A', 'border': 1, 'font_name': 'NimbusSanL', 'font_size': 8, 'font_color': '#001E5A'})

        #Set the first column width to 50

        super_columns = self._get_super_columns(options)
        y_offset = bool(super_columns.get('columns')) and 1 or 0

        sheet.write(y_offset, 0, '', title_style)

        # Todo in master: Try to put this logic elsewhere
        x = super_columns.get('x_offset', 0)
        for super_col in super_columns.get('columns', []):
            cell_content = super_col.get('string', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
            x_merge = super_columns.get('merge')
            if x_merge and x_merge > 1:
                sheet.merge_range(0, x, 0, x + (x_merge - 1), cell_content, super_col_style)
                x += x_merge
            else:
                sheet.write(0, x, cell_content, super_col_style)
                x += 1
        # for row in self.get_header(options):
        #     x = 0
        #     for column in row:
        #         colspan = column.get('colspan', 1)
        #         header_label = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
        #         if colspan == 1:
        #             sheet.write(y_offset, x, header_label, title_style)
        #         else:
        #             sheet.merge_range(y_offset, x, y_offset, x + colspan - 1, header_label, title_style)
        #         x += colspan
        #     y_offset += 1
        ctx = self._set_context(options)
        ctx.update({'no_format': True, 'print_mode': True, 'prefetch_fields': False})
        # deactivating the prefetching saves ~35% on get_lines running time
        lines = self.with_context(ctx)._get_lines(options)

        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines)

        if lines[0].get('reference'):
            sheet.set_column(1, 1, 3)
            sheet.set_column(2, 2, 50)
            sheet.set_row(7, 50)
            sheet.set_row(8, 30)
        elif self.name != 'Balance Sheet':
            sheet.set_column(1, 1, 50)
            sheet.set_row(7, 50)

        #write all data rows
        def write_data(lines, x_ind=None):
            for y in range(0, len(lines)):
                level = lines[y].get('level')
                sheet.write(y, 0, '', workbook.add_format({}))
                x_index = x_ind or 1
                y_offset = 7
                if lines[y].get('caret_options'):
                    style = level_3_style
                    col1_style = level_3_col1_style
                elif level == 0:
                    # y_offset += 1
                    style = level_0_style
                    col1_style = style
                elif level == 1:
                    style = level_1_style
                    col1_style = style
                elif level == 2:
                    style = level_2_style
                    col1_style = 'total' in lines[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
                elif level == 3:
                    style = level_3_style
                    col1_style = 'total' in lines[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
                else:
                    style = default_style
                    col1_style = default_col1_style

                if lines[y].get('note') == 'NET':
                    for x in range(1, len(lines[y]['columns']) + 1):
                        cell = lines[y]['columns'][x - 1]
                        loc_style = copy.copy(style)
                        loc_style.set_align('center')
                        workbook.formats.append(loc_style)
                        sheet.write(y + y_offset, net_x, cell.get('name', ''), loc_style)
                        net_x += 1
                else:
                    if lines[y].get('reference') or lines[0].get('reference'):
                        loc_style = copy.copy(style)
                        loc_style.set_align('left')
                        workbook.formats.append(loc_style)
                        cell_name = lines[y].get('reference')
                        if lines[y].get('reference') == 'REF':
                            sheet.merge_range(y + y_offset, x_index, y + y_offset + 1, x_index, cell_name, loc_style)
                            x_index += 1
                        else:
                            sheet.write(y + y_offset, x_index, cell_name, loc_style)
                            x_index += 1

                    # write the first column, with a specific style to manage the indentation
                    cell_name = lines[y]['name']
                    if lines[y].get('reference') == 'REF':
                        sheet.merge_range(y + y_offset, x_index, y + y_offset + 1, x_index, cell_name, style)
                        x_index += 1
                    else:
                        sheet.write(y + y_offset, x_index, cell_name, style)
                        x_index += 1

                    if lines[y].get('symbol') != 'none':
                        loc_style = copy.copy(style)
                        loc_style.set_align('center')
                        workbook.formats.append(loc_style)
                        cell_name = lines[y].get('symbol')
                        if lines[y].get('reference') == 'REF':
                            sheet.merge_range(y + y_offset, x_index, y + y_offset + 1, x_index, cell_name, loc_style)
                            x_index += 1
                        else:
                            sheet.write(y + y_offset, x_index, cell_name, loc_style)
                            x_index += 1

                    if lines[y].get('note') != 'none' and lines[y].get('note') != None:
                        loc_style = copy.copy(style)
                        loc_style.set_align('center')
                        workbook.formats.append(loc_style)
                        cell_name = lines[y].get('note')
                        if lines[y].get('reference') == 'REF':
                            sheet.merge_range(y + y_offset, x_index, y + y_offset + 1, x_index, cell_name, loc_style)
                            x_index += 1
                        else:
                            sheet.write(y + y_offset, x_index, cell_name, loc_style)
                            x_index += 1

                    # write all the remaining cells

                    for x in range(1, len(lines[y]['columns']) + 1):
                        cell = lines[y]['columns'][x - 1]
                        if lines[y].get('reference') == 'REF' or lines[y].get('header') is True:
                            if x == 1:
                                net_x = x_index
                            loc_style = copy.copy(style)
                            loc_style.set_align('center')
                            workbook.formats.append(loc_style)
                            # sheet.set_column(y + y_offset, x_index, 10)
                        else:
                            loc_style = copy.copy(style)
                            loc_style.set_align('right')
                            workbook.formats.append(loc_style)

                        if lines[y].get('colspan0') == 3 and x == 1\
                                and options['comparison']['filter'] == 'no_comparison':
                            cell_name = str()
                            for i in cell.get('name', ''):
                                cell_name += i
                                cell_name += '\n'
                            sheet.merge_range(y + y_offset, x_index, y + y_offset, x_index + 2, cell_name, loc_style)
                            x_index += 3
                        elif isinstance(cell.get('name', ''), list):
                            cell_name = str()
                            for i in cell.get('name', ''):
                                cell_name += i
                                cell_name += '\n'
                            sheet.write(y + y_offset, x_index, cell_name, loc_style)
                            x_index += 1
                        else:
                            sheet.write(y + y_offset, x_index, cell.get('name', ''), loc_style)
                            x_index += 1
            self.x_index = x_index
        # wdb.set_trace()
        if self.name == 'Balance Sheet':
            options = {'all_entries': False, 'analytic': None, 'cash_basis': None,
                       'comparison': {
                           'date_from': '2018-01-01', 'date_to': '2018-12-31', 'filter': 'no_comparison',
                           'number_period': 1,
                           'periods': [{'date_from': '2018-01-01', 'date_to': '2018-12-31', 'string': '2018'}],
                           'string': 'No comparison',
                       },
                       'date': {'date_from': '2019-01-01', 'date_to': '2019-12-31', 'filter': 'this_year',
                                'string': '2019'}, 'hierarchy': None, 'ir_filters': None, 'journals': None,
                       'partner': None, 'unfold_all': False, 'unfolded_lines': [], 'unposted_in_period': False}
            ctx = self._set_context(options)
            ctx.update({'no_format': True, 'print_mode': True, 'prefetch_fields': False})
            lines = self.env.ref('ohada_reports.account_financial_report_ohada_balancesheet').with_context(ctx)._get_lines(options)
            write_data(lines)
            lines = self.env.ref('ohada_reports.account_financial_report_ohada_balancesheet_liabilitites0').with_context(ctx)._get_lines(options)
            write_data(lines, x_ind=self.x_index)
            sheet.set_column(1, 1, 3)
            sheet.set_column(2, 2, 50)
            sheet.set_column(8, 8, 3)
            sheet.set_column(9, 9, 50)
            sheet.set_row(7, 50)
            sheet.set_row(8, 30)
        else:
            write_data(lines)
        # make header above the table
        header = {
            'year': options['date']['date_from'][0:4],
            'company': self.env.user.company_id.name,
            'vat': self.env.user.company_id.vat,
            'title': self.header and self.header + ' ' + options['date']['date_from'][0:4],
        }
        left_style = workbook.add_format(
            {'align': 'left', 'font_name': 'NimbusSanL', 'font_size': 13, 'font_color': '#001E5A'})
        right_style = workbook.add_format(
            {'align': 'right', 'font_name': 'NimbusSanL', 'font_size': 13, 'font_color': '#001E5A'})
        title_style = workbook.add_format(
            {'align': 'center', 'font_name': 'NimbusSanL', 'font_size': 13, 'font_color': '#001E5A',
             'bold': True, })
        sheet.write(2, 1, 'Désignation Entité : ' + header['year'], left_style)
        sheet.write(2, self.x_index - 1, 'Exercice clos le : ' + '31/12/' + header['year'], right_style)
        sheet.write(3, 1, "Numéro d'identification : " + (header.get('vat') or ''), left_style)
        sheet.write(3, self.x_index - 1, 'Durée (en mois) : 12', right_style)
        sheet.merge_range(5, 1, 5, self.x_index - 1, (header.get('title') or ''), title_style)

        #make double border
        sheet.merge_range(6, 1, 6, self.x_index - 1, '', top_border)
        sheet.merge_range(len(lines) + 7, 1, len(lines) + 7, self.x_index - 1, '', bottom_border)
        sheet.merge_range(7, 0, len(lines) + 6, 0, '', left_border)
        sheet.merge_range(7, self.x_index, len(lines) + 6, self.x_index, '', right_border)

        sheet.hide_gridlines(2)
        if print_bundle == True:
            return
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def print_xml(self, options):
        return {
                'type': 'ir_actions_account_report_download',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'xml',
                         'financial_id': self.env.context.get('id'),
                         }
                }

    def get_xml(self, options):
        return False

    def print_txt(self, options):
        return {
                'type': 'ir_actions_account_report_download',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'txt',
                         'financial_id': self.env.context.get('id'),
                         }
                }

    def get_txt(self, options):
        return False

    def get_html_bs(self, options, line_id=None, additional_context=None):
        '''
        return the html value of report, or html value of unfolded line
        * if line_id is set, the template used will be the line_template
        otherwise it uses the main_template. Reason is for efficiency, when unfolding a line in the report
        we don't want to reload all lines, just get the one we unfolded.
        '''

        options = {'all_entries':	False, 'analytic':	None, 'cash_basis':	None,
                    'comparison':	{
                        'date_from':	'2018-01-01', 'date_to':	'2018-12-31', 'filter':	'no_comparison', 'number_period': 1,
                        'periods': [{'date_from': '2018-01-01', 'date_to':	'2018-12-31', 'string':	'2018'}],
                        'string': 'No comparison',
                          },
                    'date':	{'date_from':	'2019-01-01', 'date_to':	'2019-12-31', 'filter':	'this_year',
                             'string':	'2019'}, 'hierarchy': None, 'ir_filters':	None,'journals': None,
                    'partner': None, 'unfold_all':	False, 'unfolded_lines': [], 'unposted_in_period': False}
        g_rcontext=dict()
        g_rcontext['lines'] = []
        reports = [self.env.ref('ohada_reports.account_financial_report_ohada_balancesheet'),
        self.env.ref('ohada_reports.account_financial_report_ohada_balancesheet_liabilitites0')]
        for report_bs in reports:
        # Check the security before updating the context to make sure the options are safe.
            self._check_report_security(options)

        # Prevent inconsistency between options and context.
            report_bs = report_bs.with_context(report_bs._set_context(options))

            templates = report_bs._get_templates()
            report_manager = report_bs._get_report_manager(options)
            report = {'name': report_bs._get_report_name(),
                      'summary': report_manager.summary,
                      'company_name': report_bs.env.user.company_id.name,
                      'type': report_bs.type,
                      'vat': report_bs.env.user.company_id.vat,
                      'year': options['date']['date_from'][0:4],
                      'header': report_bs.header and report_bs.header + ' ' + options['date']['date_from'][0:4],}
            lines = report_bs._get_lines(options, line_id=line_id)

            if options.get('hierarchy'):
                lines = report_bs._create_hierarchy(lines)

            rcontext = {'report': report,
                        'lines': {'columns_header': report_bs.get_header(options), 'lines': lines},
                        'options': options,
                        'context': report_bs.env.context,
                        'model': report_bs,
                    }

            if additional_context and type(additional_context) == dict:
                rcontext.update(additional_context)
            if report_bs.env.context.get('analytic_account_ids'):
                rcontext['options']['analytic_account_ids'] = [
                    {'id': acc.id, 'name': acc.name} for acc in report_bs.env.context['analytic_account_ids']
                ]

            render_template = templates.get('main_template', 'ohada_reports.main_template')
            if line_id is not None:
                render_template = templates.get('line_template', 'ohada_reports.line_template')
            g_rcontext['lines'].append({report_bs.name: rcontext['lines']})
        rcontext['report']['name'] = 'Balance Sheet'
        g_rcontext['report'] = rcontext['report']
        g_rcontext['options'] = rcontext['options']
        g_rcontext['model'] = rcontext['model']
        # wdb.set_trace()
        html = self.env['ir.ui.view'].render_template(
            render_template,
            values=dict(g_rcontext),
        )
        return html
