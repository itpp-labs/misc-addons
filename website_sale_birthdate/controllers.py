# -*- coding: utf-8 -*-
import datetime

from openerp.http import request
import openerp.addons.website_sale.controllers.main as main


class WebsiteSaleBirthdate(main.website_sale):

    def checkout_values(self, data=None):

        values = super(WebsiteSaleBirthdate, self).checkout_values(data=None)

        current_user = request.env.user
        print '##################'
        print current_user.id
        print request.website.user_id.id
        orm_partner = request.env['res.partner']
        print orm_partner.browse(request.website.user_id.id).birthdate
        values['checkout']['birthdate'] = datetime.date.today()

        return values
