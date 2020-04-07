# Copyright 2020 Ivan Yelizariev
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.api import Environment
from odoo.tools import lazy_property

company_original = Environment.company.fget


@lazy_property
def company(self):
    """Try to get company from website first. It affects many models and feature,
    because env.company is used to compute default values on many models
    """
    website_id = self.context.get("website_id")
    if website_id:
        return self["website"].browse(website_id).company_id
    return company_original(self)


Environment.company = company
