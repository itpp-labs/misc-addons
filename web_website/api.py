# Copyright 2020 Ivan Yelizariev
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _
from odoo.api import Environment
from odoo.exceptions import AccessError
from odoo.tools import lazy_property


@lazy_property
def website(self):
    """Like env.company, but for website"""
    website_ids = self.context.get("allowed_website_ids", [])
    if website_ids:
        if not self.su:
            user_website_ids = self.user.backend_website_ids.ids
            if any(cid not in user_website_ids for cid in website_ids):
                raise AccessError(_("Access to unauthorized or invalid websites."))
        return self["website"].browse(website_ids[0])
    return self.user.backend_website_id


@lazy_property
def websites(self):
    """Like env.companies, but for websites"""
    website_ids = self.context.get("allowed_website_ids", [])
    if website_ids:
        if not self.su:
            user_website_ids = self.user.website_ids.ids
            if user_website_ids and any(
                cid not in user_website_ids for cid in website_ids
            ):
                raise AccessError(_("Access to unauthorized or invalid websites."))
        return self["website"].browse(website_ids)
    return self.user.backend_website_ids


Environment.website = website
Environment.websites = websites
