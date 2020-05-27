# -*- coding: utf-8 -*-
# © 2017-NOW ERGOBIT Consulting (http://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
    
 
class ResPartner(models.Model):
    _inherit  = 'res.partner'

    company_executive_id = fields.Many2one('res.company', string="Société dirigée", ondelete='restrict')
    company_administrative_id = fields.Many2one('res.company', string="Société administrée", ondelete='restrict')
    has_own_accounting = fields.Boolean(string="Une comptabilité distincte est tenue?")
