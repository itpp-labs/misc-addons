# -*- coding: utf-8 -*-

from openerp import api
from openerp import models


class ResPartnerStripName(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def write(self, vals):
        for r in self:
            r.write_one(vals)
        return True

    @api.multi
    def write_one(self, vals):
        self.ensure_one()
        vals = self._check_name_field(vals)
        return super(ResPartnerStripName, self).write(vals)

    @api.model
    def create(self, vals):
        vals = self._check_name_field(vals)
        return super(ResPartnerStripName, self).create(vals)

    def _check_name_field(self, vals):
        if vals.get('name'):
            vals['name'] = vals['name'].strip().strip('"')
        return vals
