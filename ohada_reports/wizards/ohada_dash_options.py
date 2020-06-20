from odoo import models, fields, api
from datetime import datetime


class DashboardOptions(models.TransientModel):
    """
    This wizard is used to change dashboard options options
    """
    _name = 'ohada.dash.options'
    _description = 'Change dashboard options'

    current_year = fields.Integer(string='Current year', default=datetime.now().year)

    def change_options(self):
        import wdb;wdb.set_trace()
        dashes = self.env['ohada.dash'].search([])
        for dash in dashes:
            dash.current_year = self.current_year
