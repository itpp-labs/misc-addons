from odoo import models, fields, api
from datetime import datetime
import json
from odoo.http import content_disposition, request
import base64, io, xlsxwriter

class DashboardPrintBundle(models.TransientModel):
    """
    This wizard is used to change dashboard options options
    """
    _name = "ohada.dash.print.bundle"
    _description = 'Dashboard print bundle'

    company_name = fields.Char(
        string="Company name",
        readonly=True,
        default=lambda s: s.env.ref('ohada_reports.ohada_dashboard_view_your_company').company_id.name)
    dash_year = fields.Char(
        string="Year",
        readonly=True,
        default=lambda s: s.env.ref('ohada_reports.ohada_dashboard_options').sudo().current_year)
    all_entries = fields.Char(
        string="Posted",
        readonly=True,
        default=lambda s: s.env.ref('ohada_reports.ohada_dashboard_options').sudo().all_entries)

    balance_assets = fields.Boolean(string="Balance Sheet - Assets")
    balance_liabilitities = fields.Boolean(string="Balance Sheet - Liabilitities")
    profit_loss = fields.Boolean(string="Profit & Loss")
    cashflow = fields.Boolean(string="Cashflow")
    notes = fields.Boolean(string="Notes")

    def print_pdf(self, *context):
        report = self.env['ohada.financial.html.report']
        options = report.make_temp_options(int(self.dash_year))

        bundle_items = self.get_bundle_reports_ids()
        if not len(bundle_items):
            return True

        report_obj = self.env["ohada.financial.html.report"].sudo()
        report_obj = report_obj.browse(1)
        pdf = report_obj.print_bundle_pdf(options, bundle_items)
        attachment = self.env['ir.attachment'].create({
                'datas': base64.b64encode(pdf),
                'name': 'New pdf report',
                'datas_fname': 'report.pdf',
                'type': 'binary'
        })
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': attachment.website_url
        }

    def print_xlsx(self, *context):
        dash = self.env.ref('ohada_reports.ohada_dashboard_view_your_company')
        report = self.env['ohada.financial.html.report']
        options = report.make_temp_options(dash.current_year)

        bundle_items = self.get_bundle_reports_ids()
        xlsx = self.print_bundle_xlsx(options, bundle_items)
        attachment = self.env['ir.attachment'].create({
                'datas': base64.b64encode(xlsx),
                'name': 'New xlsx report',
                'datas_fname': 'report.xlsx',
                'type': 'binary'
        })
        return {
            'type': 'ir.actions.act_url',
            'name': attachment.datas_fname,
            'url': attachment.local_url
        }

    def get_bundle_reports_ids(self):
        bundle_items = {
            'Balance Sheet - Assets': self.balance_assets,
            'Balance Sheet - Liabilitites': self.balance_liabilitities,
            'Profit & Loss': self.profit_loss,
            'Cashflow': self.cashflow,
            'Notes': self.notes
        }
        choosen_items = []
        for i in self.env['ohada.financial.html.report'].search([('type', '=', 'main')]):
            if bundle_items.get(i.name, 0):
                choosen_items.append(str(i.id))
        if bundle_items.get("Notes", 0):
            choosen_items.append('notes')
        return ','.join(choosen_items)

    def close_button(self):
        return {'type': 'ir.actions.act_window_close'}

    def print_bundle_xlsx(self, options, reports_ids=None):
        response = {}
        reports_ids = reports_ids.split(',')
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        for report_id in reports_ids:
            if report_id != 'notes':
                self.env['ohada.financial.html.report'].browse(int(report_id)).get_xlsx(options, response, print_bundle=True, workbook=workbook)
            else:
                options['comparison']['filter'] = 'previous_period'
                for report in self.env['ohada.financial.html.report'].search([('type', '=', 'note'), ('secondary', '=', False)]):
                    options = report._get_options(options)
                    report._apply_date_filter(options)
                    if report.code in ['N1']:
                        options['comparison']['filter'] = 'no_comparison'
                        options = report._get_options(options)
                        report._apply_date_filter(options)
                    report.get_xlsx(options, response, print_bundle=True, workbook=workbook)


        workbook.close()
        output.seek(0)
        temporary_variable = output.read()
        output.close()
        return temporary_variable
