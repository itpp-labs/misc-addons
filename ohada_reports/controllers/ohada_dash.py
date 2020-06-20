# Copyright 2020 Vildan Safin <https://www.it-projects.info/team/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import route, request, Controller
import urllib.parse

class OhadaDashController(Controller):

    @route(['/get_report_values'], type='json', auth='public')
    def get_reports_vals(self, **kw):
        
        return {
        }
