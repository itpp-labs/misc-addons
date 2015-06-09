# -*- coding: utf-8 -*-

from openerp import models, fields, api


class res_partner_strip_name(models.Model):
    _inherit = 'res.partner'

    @api.one
    def write(self, vals):
        vals = self._check_name_field(vals)
        return super(res_partner_strip_name, self).write(vals)

    @api.model
    def create(self, vals):
        vals = self._check_name_field(vals)
        return super(res_partner_strip_name, self).create(vals)

    def _check_name_field(self, vals):
        if vals.get('name'):
            vals['name'] = vals['name'].strip().strip('"')
        return vals
