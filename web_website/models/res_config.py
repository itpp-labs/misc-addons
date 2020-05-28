# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2020 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import api, fields, models


class WebWebsiteConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    group_multi_website = fields.Boolean(
        string="Multi Website for Backend",
        help="Show Website Switcher in backend",
        implied_group="web_website.group_multi_website",
    )

    @api.multi
    def open_template_user(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        IrProperty = self.env["ir.property"].sudo()
        ResUsers = self.env["res.users"].sudo()

        # search for all properties for that case
        param_id = IrConfigParameter.search(
            [("key", "=", "auth_signup.template_user_id")], limit=1
        )
        field = self.env["ir.model.fields"].search(
            [("model", "=", "ir.config_parameter"), ("name", "=", "value")], limit=1
        )
        prop_ids = IrProperty.search(
            [
                ("fields_id", "=", field.id),
                ("res_id", "=", "{},{}".format(IrConfigParameter._name, param_id.id)),
            ]
        )

        website_id = ResUsers.browse(self._context["uid"]).backend_website_id
        # Is it needed?? if param_id.value in prop_ids.filtered(lambda p: not p.website_id).mapped('value_text') and ...
        if website_id not in prop_ids.mapped("website_id"):
            # Template user was not created/set for current website
            website_id.create_new_template_user_id()
        return super(WebWebsiteConfigSettings, self).open_template_user()
