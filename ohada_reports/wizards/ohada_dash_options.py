from odoo import models, fields, api
from datetime import datetime


class DashboardOptions(models.TransientModel):
    """
    This wizard is used to change dashboard options options
    """
    _name = 'ohada.dash.options'
    _description = 'Change dashboard options'

    current_year = fields.Selection([(num, str(num)) for num in range((datetime.now().year) - 5, (datetime.now().year)+1 )],
             string='Year', default=datetime.now().year)
    all_entries = fields.Boolean(string="Status of journal entries")

    @api.multi
    def change_options(self):
        # Setting new options
        options = self.env.ref('ohada_reports.ohada_dashboard_options').sudo()
        options.current_year = int(self.current_year)
        options.all_entries = self.all_entries
        # Loading dashboard with new options
        server_action = self.env.ref('ohada_reports.ohada_action_dash_server').read()[0]
        server_action['target'] = 'main'
        server_action['context'] = {'change_options': True}
        return server_action
