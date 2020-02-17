# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import fields, models


class WebsiteDependent(models.Model):
    _name = "test.website_dependent"

    foo = fields.Char(company_dependent=True, website_dependent=True)


class CompanyDependent(models.Model):
    _name = "test.company_dependent"

    foo = fields.Char(company_dependent=True)
