from odoo import models, fields, api
from datetime import datetime
import json

class DashboardPrintBundle(models.TransientModel):
    """
    This wizard is used to change dashboard options options
    """
    _name = "ohada.dash.print.bundle"
    _description = 'Dashboard print bundle'

    reports = fields.Text(string="Main reports", compute="_get_main_reports")

    @api.multi
    def _get_main_reports(self):
        import wdb;wdb.set_trace()
        data = []
        for report in self.env['ohada.financial.html.report'].search([('type', '=', 'main')]):
            data.append({'name': report.name, 'id': report.id})
        dash = self.env.ref('ohada_reports.ohada_dashboard_view_your_company')
        self.reports = json.dumps({
            'reports': data,
            'company_name': dash.company_id.name,
            'year': dash.current_year
        })
