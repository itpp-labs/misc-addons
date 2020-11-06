from odoo import models, fields, api
from datetime import datetime
import json
from odoo.http import content_disposition, request
import base64, io, xlsxwriter
import codecs
import os
import tempfile                     
from PyPDF2 import PdfFileMerger, PdfFileReader

import logging
_logger = logging.getLogger(__name__)

class DashboardPrintBundle(models.TransientModel):
    """
    This wizard is used to download picked reports
    """
    _name = "ohada.dash.print.bundle"
    _description = 'Dashboard print bundle'

    company_name = fields.Char(
        string="Company name",
        readonly=True,
        default=lambda s: s.env.user.company_id.name)
#        default=lambda s: s.env.ref('ohada_reports.ohada_dashboard_view_your_company').company_id.name)
    dash_year = fields.Char(
        string="Year",
        readonly=True,
        default=lambda s: s.env.ref('ohada_reports.ohada_dashboard_options').sudo().current_year)
    all_entries = fields.Char(
        string="All journal entries",
        readonly=True,
        default=lambda s: s.env.ref('ohada_reports.ohada_dashboard_options').sudo().all_entries)

    cover_sheet = fields.Boolean(string="Coverpage and Sheets")    
    general_info = fields.Boolean(string="General Information")
    balance_sheet = fields.Boolean(string="Balance Sheet")
#    balance_assets = fields.Boolean(string="Balance Sheet - Assets")
#    balance_liabilitities = fields.Boolean(string="Balance Sheet - Liabilitities")
    profit_loss = fields.Boolean(string="Profit & Loss")
    cashflow = fields.Boolean(string="Cashflow")
    notes = fields.Boolean(string="Notes")
    xlsx_bundle = fields.Binary('Xlsx file')

    def only_BS_picked(self):
#        return self.balance_liabilitities and self.balance_assets and not (self.profit_loss or self.cashflow or self.notes)
        return self.balance_sheet and not (self.general_info or self.cover_sheet or self.profit_loss or self.cashflow or self.notes)

    def is_BS_format_landscape(self):
        return True if self.env.ref('ohada_reports.ohada_report_balancesheet_0').print_format == 'landscape' else False

    def print_pdf(self, *context):
        report = self.env['ohada.financial.html.report']
        options = report.make_temp_options(int(self.dash_year))
        # When only BS picked
        if self.only_BS_picked():
            BS_report = self.env['ohada.dash'].search([('report_code', '=', 'BS')])
            return BS_report.preview_pdf()

        bundle_items = self.get_bundle_reports_ids()
        if not len(bundle_items):
            return True

        report_obj = self.env["ohada.financial.html.report"].sudo()
        report_obj = report_obj.browse(1)

        # 'make_pdfs' method makes pdfs and merges them in one file
        # 'make_pdfs' method returns number of pages
        #path = '/var/lib/odoo/ohada_pdfs'                                  #E- do not work in windows os
        path = tempfile.gettempdir() or '/tmp'                              #E+
        
        pages_num = self.make_pdfs(options, bundle_items.split(','), path, pages=len(bundle_items.split(',')))
        # Create attachment from 'result.pdf' file
        with open('%s/result.pdf' % (path), "rb") as f:
            pdf = base64.b64encode(f.read())
            attachment = self.env['ir.attachment'].create({
                    'datas': pdf,
                    'name': 'New pdf report',
                    'datas_fname': 'report.pdf',
                    'type': 'binary'
            })
            self.make_disclosure(pages_num, pdf)
        # Delete all created pdf's from 'path'
        self.delete_pdfs(path)
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': attachment.local_url
        }

    def make_pdfs(self, options, bundle_items, path, pages=0):
        reports = []
        # Searching for reports from 'bundle_items'
        for item in bundle_items:
            # Get other reports
            if item != 'notes':
                reports.append(self.env['ohada.financial.html.report'].browse(int(item)))
            else:
                # Get notes
                notes = self.env['ohada.financial.html.report'].search([('type', '=', 'note'), ('secondary', '=', False)])
                options['comparison']['filter'] = 'previous_period'
                company = self.env['res.users'].browse(self._context.get('uid')).company_id
                year = options['date'].get('string')
                for note in notes:
                    note_relevance = self.env['note.relevance'].search([('note_report_id', '=', note.id),
                                                                                ('fiscalyear', '=', year),
                                                                                ('company_id', '=', company.id)])
                    if note_relevance and note_relevance.relevant:
                        reports.append(note)
        # Here will be stored pdf file names
        pdf_names = []

        for i, report in enumerate(reports):
            # Options for notes
            if report.type == 'note':
                options = report._get_options(options)
                report._apply_date_filter(options)
            # Create pdf
            _logger.info('Started creating report pdf: %s' % (report.shortname))
            pdf = report.get_pdf(
                options, horizontal=True if report.print_format == 'landscape' else False,
                pages={'topage': len(reports), 'page': len(pdf_names) + 1}
            )
            # Save pdf in 'path' folder
            with open("%s/%s.pdf" % (path, i + 1),'wb') as f:
                f.write(codecs.decode(base64.b64encode(pdf), "base64"))
            _logger.info('Created report pdf: %s' % (report.shortname))
            _logger.info('%s path: %s/%s.pdf' % (report.shortname, path, i + 1))
            # Save pdf name
            pdf_names.append('%s.pdf' % (i + 1))

        # Merge all created pdf's in one
        merger = PdfFileMerger()
        for name in pdf_names:
            _logger.info('Merged: %s.pdf.' % (name))
            merger.append(PdfFileReader(open('%s/%s' % (path, name), 'rb')), import_bookmarks=False)

        # Save pdf in 'result.pdf'
        merger.write('%s/result.pdf' % (path))
        merger.close()
        # Returning number of pages
        return len(reports)

    def delete_pdfs(self, path):
        for pdf in [a for a in os.listdir(path) if a.endswith(".pdf")]:
            os.remove('%s/%s' % (path, pdf))

    def make_disclosure(self, pages_num, pdf):
        company = self.env['res.users'].browse(self._context.get('uid')).company_id
        disclosure = self.env['ohada.disclosure'].search([('company_id', '=', company.id),
                                                          ('fiscalyear_id', '=', self.dash_year),
                                                          ('bundle_report_file_pdf', '!=', False)])
        if not disclosure:
            disclosure = self.env['ohada.disclosure'].search([('company_id', '=', company.id),
                                                              ('fiscalyear_id', '=', self.dash_year)])
            if not disclosure:
                self.env['ohada.disclosure'].create({'bundle_report_file_pdf': pdf,
                                                     'company_id': company.id,
                                                     'status': 'report_available',
                                                     'fiscalyear_id': self.dash_year,
                                                     'number_of_pages': pages_num})
            else:
                disclosure.write({'bundle_report_file_pdf': pdf, 'number_of_pages': pages_num})

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
                'type': 'url'
        })
        self.xlsx_bundle = base64.b64encode(xlsx)
        return {
            'type': 'ir.actions.act_url',
            'name': 'bundle',
            'url': '/web/content/ohada.dash.print.bundle/%s/xlsx_bundle/xlsx_bundle.xlsx?download=true' %(self.id),
        }

    def print_bundle_xlsx(self, options, reports_ids=None):
        response = {}
        reports_ids = reports_ids.split(',')
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        if self.only_BS_picked() and self.env.user.company_id.bs_report_format == 'landscape':
            report_obj = self.env.ref('ohada_reports.ohada_report_balancesheet_0')
            report_obj.get_xlsx(options, response, print_bundle=True, workbook=workbook)
        else:
            for report_id in reports_ids:
                if report_id and report_id != 'notes':
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

    def get_bundle_reports_ids(self):
        bundle_items = {}
        # If general information choosen,
        # then print all available reports
        if self.general_info:
            self.balance_sheet = True
            self.profit_loss = True
            self.cashflow = True
            self.notes = True
        #if self.env['res.users'].browse(self._context.get('uid')).company_id.bs_report_format == 'landscape':
        if self.env.user.company_id.bs_report_format == 'landscape':
            bundle_items.update({
                'BS': self.balance_sheet
            })
        else:
            bundle_items.update({
                'BS1': self.balance_sheet,
                'BS2': self.balance_sheet
            })
        bundle_items.update({
            'PL': self.profit_loss,
            'CF': self.cashflow,
            'N': self.notes
        })
        choosen_items = []
#        for i in self.env['ohada.financial.html.report'].search([('type', '=', 'main')]):
        for i in self.env['ohada.financial.html.report'].search(['|', ('code', '=', 'BS'), ('type', '=', 'main')]):
#        for i in self.env['ohada.financial.html.report'].search([('type', '!=', 'note')]):
            #if bundle_items.get(i.name, 0):
            if bundle_items.get(i.code, 0):
                choosen_items.append(str(i.id))
        if bundle_items.get("N", 0):
            choosen_items.append('notes')
        return ','.join(choosen_items)

    def close_button(self):
        return {'type': 'ir.actions.act_window_close'}

