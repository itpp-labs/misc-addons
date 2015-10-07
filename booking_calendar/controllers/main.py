from openerp import http
from openerp.http import request

from openerp.addons.website_booking_calendar.controllers.main import website_booking_calendar as controller


class website_booking_calendar(controller):

    def _get_template(self, params):
        if params.get('backend', False):
            return 'website_booking_calendar.iframe'
        else:
            return super(website_booking_calendar, self)._get_template(params)


        

