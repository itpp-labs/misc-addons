# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):

    _inherit = "res.users"

    backend_website_id = fields.Many2one("website", "Current Backend Website")
    backend_website_ids = fields.Many2many(
        "website",
        "Allowed Backend Websites",
        help="Computed automatically based on Current Company field",
        compute="_compute_backend_website_ids",
    )
    backend_websites_count = fields.Integer(compute="_compute_backend_website_ids")

    @api.model
    def _get_company(self):
        """Try to get company from website first. It affects many models and feature,
        because it's used in _company_default_get which is used to compute
        default values on many models
        """
        website_id = self.env.context.get("website_id")
        if website_id:
            return self.env["website"].browse(website_id).company_id
        return super(ResUsers, self)._get_company()

    @api.model
    def _search_company_websites(self, company_id):
        return self.env["website"].search(
            [("company_id", "in", [False] + [company_id])]
        )

    def _compute_backend_website_ids(self):
        for r in self:
            websites = self._search_company_websites(r.company_id.id)
            r.backend_website_ids = websites
            r.backend_websites_count = len(websites)

    def write(self, vals):
        if "company_id" in vals and "backend_website_id" not in vals:
            websites = self._search_company_websites(vals["company_id"])
            if len(websites) == 1:
                vals["backend_website_id"] = websites.id
            else:
                vals["backend_website_id"] = None
        return super(ResUsers, self).write(vals)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if self.company_id:
            if self.backend_website_id.company_id != self.company_id:
                self.backend_website_id = None

        self._compute_backend_website_ids()

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
                    _("Current website doesn't belong to Current Company")
                )

    def __init__(self, pool, cr):
        # don't save result of super to return after extension due to E0101, return-in-init
        super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(["backend_website_id"])
