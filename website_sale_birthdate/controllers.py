# -*- coding: utf-8 -*-
import datetime

import openerp.addons.website_sale.controllers.main as main


class WebsiteSaleBirthdate(main.website_sale):

    def checkout_values(self, data=None):

        values = super(WebsiteSaleBirthdate, self).checkout_values(data=None)
        values['checkout']['birthdate'] = datetime.date.today()

        return values
