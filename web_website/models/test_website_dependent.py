# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models

FIELDS = ["foo", "user_id"]


class WebsiteDependent(models.Model):
    _inherit = "website_dependent.mixin"
    _name = "test.website_dependent"
    _description = "Model for testing web_website module"

    name = fields.Char()
    foo = fields.Char(company_dependent=True, website_dependent=True)
    user_id = fields.Many2one(
        "res.users", company_dependent=True, website_dependent=True
    )

    @api.model
    def create(self, vals):
        res = super(WebsiteDependent, self).create(vals)
        # make value company independent
        for f in FIELDS:
            res._force_default(f, vals.get(f))
        return res

    def write(self, vals):
        res = super(WebsiteDependent, self).write(vals)

        if "name" in vals:
            fields_to_update = FIELDS
        else:
            fields_to_update = [f for f in FIELDS if f in vals]
        for f in fields_to_update:
            self._update_properties_label(f)

        return res


class CompanyDependent(models.Model):
    _name = "test.company_dependent"
    _description = "Test Class with company_dependent fields"

    foo = fields.Char(company_dependent=True)
    user_id = fields.Many2one("res.users", company_dependent=True)
