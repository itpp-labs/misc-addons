from odoo import models, fields, api
from datetime import datetime


class DashboardOptions(models.TransientModel):
    """
    This wizard is used to change dashboard options options
    """
    _name = 'ohada.dash.options'
    _description = 'Change dashboard options'

    current_year = fields.Char(string='Current year', default=str(datetime.now().year))
    all_entries = fields.Boolean(string="Status of journal entries")

    @api.multi
    def change_options(self):
        # Setting new options
        options = self.env.ref('ohada_reports.ohada_dashboard_options').sudo()
        options.current_year = int(self.current_year)
        options.all_entries = self.all_entries
        # Loading dashboard with new options
        return self.env.ref('ohada_reports.ohada_action_dash').sudo().read()[0]
