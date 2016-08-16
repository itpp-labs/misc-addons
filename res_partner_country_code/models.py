# -*- coding: utf-8 -*-
from openerp import models, fields


class ResPartnerCountryCode(models.Model):
    _inherit = 'res.partner'

    def default_country_id(self):
        email = self.env.context.get('default_email', False)
        if email:
            top_level_domain = email.split(".")[-1]
            if len(top_level_domain) == 2:
                if top_level_domain == 'uk':
                    top_level_domain = 'GB'
                country = self.env['res.country'].search([('code', '=', top_level_domain.upper())])
                if country:
                    return country.id

    country_id = fields.Many2one(default=default_country_id)
