# Copyright 2018,2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):

    _inherit = "res.users"

    backend_website_id = fields.Many2one("website", "Default Backend Website")
    backend_website_ids = fields.Many2many(
        "website",
        string="Allowed Backend Websites",
        relation="rel_users_backend_website_ids",
        help="Computed automatically based on active Companies and Accessible Backend Websites",
        compute="_compute_backend_website_ids",
    )
    access_backend_website_ids = fields.Many2many(
        "website",
        string="Accessible Backend Websites",
        relation="rel_users_access_backend_website_ids",
        help="Keep Empty to allow all Websites",
    )

    def _search_company_websites(self, company_ids):
        self.ensure_one()
        domain = [("company_id", "in", [False] + company_ids)]
        if self.access_backend_website_ids:
            domain.append(("id", "in", self.access_backend_website_ids.ids))
        return self.env["website"].search(domain)

    def _compute_backend_website_ids(self):
        for r in self:
            r.backend_website_ids = self._search_company_websites(
                self.env.companies.ids
            )

    def write(self, vals):
        if "company_id" in vals and "backend_website_id" not in vals:
            websites = self._search_company_websites([vals["company_id"]])
            if len(websites) == 1:
                vals["backend_website_id"] = websites.id
            else:
                vals["backend_website_id"] = None
        return super(ResUsers, self).write(vals)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if self.company_id:
            if (
                self.backend_website_id.company_id
                and self.backend_website_id.company_id != self.company_id
            ):
                self.backend_website_id = None

        return {
            "domain": {
                "backend_website_id": [("company_id", "in", self.company_id.ids or [])]
            }
        }

    @api.constrains("company_id", "backend_website_id")
    def _check_backend_website_in_current_company(self):
        for record in self:
            if (
                record.backend_website_id
                and record.company_id
                and record.backend_website_id.company_id
                and record.backend_website_id.company_id != record.company_id
            ):
                raise ValidationError(
                    _("Default website doesn't belong to Default Company")
                )

    def __init__(self, pool, cr):
        # don't save result of super to return after extension due to E0101, return-in-init
        super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(["backend_website_id"])
