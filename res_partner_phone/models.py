# -*- coding: utf-8 -*-
from openerp import api
from openerp import models


class ResPartnerPhone(models.Model):
    _inherit = 'res.partner'

    @api.depends('is_company', 'name', 'parent_id.name', 'type', 'company_name', 'mobile', 'phone')
    def _compute_display_name(self):
        return super(ResPartnerPhone, self)._compute_display_name()

    @api.multi
    def name_get(self):
        result = dict(super(ResPartnerPhone, self).name_get())
        records = self.browse(result.keys())
        for r in records:
            if r.mobile:
                result[r.id] += ' (' + r.mobile + ')'
            if r.phone:
                result[r.id] += ' (' + r.phone + ')'
        return result.items()
