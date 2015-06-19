# -*- coding: utf-8 -*-
import datetime

from openerp.http import request
import openerp.addons.website_sale.controllers.main as main


class WebsiteSaleBirthdate(main.website_sale):

    def checkout_values(self, data=None):

        values = super(WebsiteSaleBirthdate, self).checkout_values(data)

        current_user = request.env.user

        public = request.env.ref('base.public_partner')
        orm_partner = request.env['res.partner'].sudo(public)

        # if user is activated
        if current_user.active:
            partner_id = current_user.partner_id

            partner_birthdate = orm_partner.browse(int(partner_id)).birthdate

            if partner_birthdate:
                values['checkout']['birthdate'] = partner_birthdate

        return values

    main.website_sale.mandatory_billing_fields.append('birthdate')
