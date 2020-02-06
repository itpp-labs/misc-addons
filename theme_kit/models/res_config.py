# Copyright 2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016,2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import hashlib

from openerp import api, fields, models

FIELD_PARAM_ID_LIST = [
    ("theme_id", "theme_kit.current_theme_id"),
    ("favicon_id", "theme_kit.current_favicon_id"),
]
FIELD_PARAM_STR_LIST = [
    ("page_title", "web_debranding.new_title"),
    ("system_name", "web_debranding.new_name"),
]

CUSTOM_CSS_ARCH = """<?xml version="1.0"?>
<t t-name="theme_kit.custom_css">
%s
</t>
"""


class Config(models.TransientModel):

    _name = "theme_kit.config"
    _inherit = "res.config.settings"

    theme_id = fields.Many2one("theme_kit.theme", string="Color Scheme")
    favicon_id = fields.Many2one("ir.attachment", string="Favicon")

    page_title = fields.Char(
        "Page Title",
        help="""Anything you want to see in page title, e.g.
* CompanyName
* CompanyName's Portal
* CompanyName's Operation System
* etc.
    """,
    )
    system_name = fields.Char(
        "System Name",
        help="""e.g.
* CompanyName's Portal
* CompanyName's Operation System
* etc.
    """,
    )
    company_logo = fields.Binary(
        "Company Logo",
        help="Due to browser cache, old logo may be still shown. To fix that, clear browser cache",
    )

    wallpapers_count = fields.Integer("Wallpapers", readonly=True)

    @api.multi
    def get_default_wallpapers_count(self, fields):
        wallpapers_count = self.env["ir.attachment"].search_count(
            [("use_as_background", "=", True)]
        )
        return {"wallpapers_count": wallpapers_count}

    @api.multi
    def get_default_company_logo(self, fields):
        return {"company_logo": self.env.user.company_id.logo}

    @api.multi
    def set_company_logo(self):
        self.env.user.company_id.logo = self.company_logo

    @api.multi
    def get_default_ids(self, fields):
        res = {}
        for field, param in FIELD_PARAM_ID_LIST:
            value = self.env["ir.config_parameter"].get_param(param)
            try:
                res[field] = int(value)
            except:
                pass
        return res

    @api.multi
    def set_ids(self):
        for field, param in FIELD_PARAM_ID_LIST:
            self.env["ir.config_parameter"].set_param(
                param, getattr(self, field).id or ""
            )

    @api.multi
    def get_default_strs(self, fields):
        res = {}
        for field, param in FIELD_PARAM_STR_LIST:
            value = self.env["ir.config_parameter"].get_param(param)
            res[field] = value
        return res

    @api.multi
    def set_strs(self):
        for field, param in FIELD_PARAM_STR_LIST:
            self.env["ir.config_parameter"].set_param(param, getattr(self, field) or "")

    @api.multi
    def set_theme(self):
        custom_css = self.env.ref("theme_kit.custom_css")
        code = ""
        if self.theme_id:
            code = self.theme_id.code
        arch = CUSTOM_CSS_ARCH % code
        custom_css.write({"arch": arch})

    def _attachment2url(self, att):
        sha = hashlib.sha1(getattr(att, "__last_update")).hexdigest()[0:7]
        return "/web/image/{}-{}".format(att.id, sha)

    @api.multi
    def set_favicon(self):
        url = ""
        if self.favicon_id:
            url = self.favicon_id.url or self._attachment2url(self.favicon_id)
        self.env["ir.config_parameter"].set_param("web_debranding.favicon_url", url)
