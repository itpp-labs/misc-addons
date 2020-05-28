# Copyright 2020 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, models


class Website(models.Model):
    _inherit = "website"

    @api.model
    def create(self, vals):
        website = super(Website, self).create(vals)
        website.create_new_template_user_id()
        return website

    @api.multi
    def create_new_template_user_id(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        user_id = IrConfigParameter.get_param("auth_signup.template_user_id", "False")
        user_id = self.env["res.users"].sudo().browse(user_id and int(user_id))
        for record in self:
            company_id = record.company_id.id
            new_user_id = user_id.sudo().copy(
                {
                    "login": "{} - {}".format(user_id.login, record.name),
                    "company_id": company_id,
                    "company_ids": [(6, 0, [company_id])],
                    "backend_website_ids": [(6, 0, record.ids)],
                }
            )
            IrConfigParameter.with_context(dict(website_id=record.id)).set_param(
                "auth_signup.template_user_id", new_user_id.id
            )
