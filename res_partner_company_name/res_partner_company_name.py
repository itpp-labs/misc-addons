# -*- coding: utf-8 -*-
from openerp import api,models, fields

class res_partner(models.Model):
    _inherit = "res.partner"

    @api.one
    def _get_company_name(self):
        name = self.name
        if not self.is_company and self.parent_id:
            name = self.parent_id.name
        print '_get_company_name', name
        self.company_name = name

    company_name = fields.Char('Company name', compute=_get_company_name)
