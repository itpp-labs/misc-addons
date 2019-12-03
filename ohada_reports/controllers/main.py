# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import content_disposition, request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape

import json
import wdb

class FinancialReportController(http.Controller):

    @http.route('/ohada_reports', type='http', auth='user', methods=['POST'], csrf=False)
    def get_report(self, model, options, output_format, token, financial_id=None, **kw):
        uid = request.session.uid
        report_obj = request.env[model].sudo(uid)
        options = json.loads(options)
        if financial_id and financial_id != 'null':
            report_obj = report_obj.browse(int(financial_id))
        report_name = report_obj.get_report_filename(options)
        try:
            if output_format == 'pdf_bundle':
                response = request.make_response(
                    report_obj.print_bundle_pdf(options),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', content_disposition('general_report.pdf'))
                    ]
                )
            elif output_format == 'xlsx_bundle':
                response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', content_disposition('general_report.xlsx'))
                    ]
                )
                report_obj.print_bundle_xlsx(options, response)
            elif output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', content_disposition(report_name + '.xlsx'))
                    ]
                )
                report_obj.get_xlsx(options, response)
            elif output_format == 'pdf' and kw.get('horizontal') == 'True':
                response = request.make_response(
                    report_obj.get_pdf(options, horizontal=True),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', content_disposition(report_name + '.pdf'))
                    ]
                )
            elif output_format == 'pdf':
                response = request.make_response(
                    report_obj.get_pdf(options),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', content_disposition(report_name + '.pdf'))
                    ]
                )
            elif output_format == 'xml':
                content = report_obj.get_xml(options)
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'application/vnd.sun.xml.writer'),
                        ('Content-Disposition', content_disposition(report_name + '.xml')),
                        ('Content-Length', len(content))
                    ]
                )
            elif output_format == 'xaf':
                content = report_obj.get_xaf(options)
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'application/vnd.sun.xml.writer'),
                        ('Content-Disposition', 'attachment; filename=' + content_disposition(report_name + '.xaf;')),
                        ('Content-Length', len(content))
                    ]
                )
            elif output_format == 'txt':
                content = report_obj.get_txt(options)
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'text/plain'),
                        ('Content-Disposition', content_disposition(report_name + '.txt')),
                        ('Content-Length', len(content))
                    ]
                )
            elif output_format == 'csv':
                content = report_obj.get_csv(options)
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'text/csv'),
                        ('Content-Disposition', 'attachment; filename=' + content_disposition(report_name + '.csv;')),
                        ('Content-Length', len(content))
                    ]
                )
            elif output_format == 'zip':
                content = report_obj._get_zip(options)
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'application/zip'),
                        ('Content-Disposition', 'attachment; filename=' + content_disposition(report_name + '.zip')),
                    ]
                )
                # Adding direct_passthrough to the response and giving it a file
                # as content means that we will stream the content of the file to the user
                # Which will prevent having the whole file in memory
                response.direct_passthrough = True
            response.set_cookie('fileToken', token)
            return response
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
