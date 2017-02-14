# -*- coding: utf-8 -*-
from openerp import api, models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def _get_company_name(self):
        for r in self:
            r._get_company_name_one()
        return True

    @api.multi
    def _get_company_name_one(self):
        self.ensure_one()
        name = self.name
        if not self.is_company and self.parent_id:
            name = self.parent_id.name
        self.company_name = name

    company_name = fields.Char('Company name', compute=_get_company_name)
