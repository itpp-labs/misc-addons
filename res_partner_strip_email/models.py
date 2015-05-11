# -*- coding: utf-8 -*-

from openerp import models, fields, api

class res_partner_strip_email(models.Model):
    _inherit = 'res.partner'
    
    @api.one
    def write(self, vals):
        if 'email' in vals:
             vals['email']=vals['email'].strip()
        res = super(res_partner_strip_email, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        if vals['email']:
            vals['email']=vals['email'].strip()
        res = super(res_partner_strip_email, self).create(vals)
        return res
