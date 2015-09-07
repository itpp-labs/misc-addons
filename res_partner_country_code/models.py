# -*- coding: utf-8 -*-
from openerp import models, fields

class res_partner_country_code(models.Model):
    _inherit = 'res.partner'

    def get_country_name(self):
        email = self.env.context.get('default_email', False)
        if email:
            top_level_domain = email.split(".")[-1]
            country_name = self.env['res.country'].search([('code', '=', top_level_domain.upper())])[0]
            return country_name

    country_id = fields.Many2one('res.country', 'Country', ondelete='restrict', default=get_country_name)

