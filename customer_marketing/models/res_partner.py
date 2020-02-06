# -*- coding: utf-8 -*-
from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    family = fields.Text(
        string="Family", help=u"Notes on family members – wife and kids"
    )
    occupation = fields.Text(string="Occupation", help="What do they do for a living")
    recreation = fields.Text(
        string="Recreation", help="List of things they enjoy doing"
    )
    motivation = fields.Text(
        string="Motivation", help="What do they like about stuff/mktg"
    )
    animals = fields.Text(string="Animals", help="Place to note any pets")
    teams = fields.Text(string="Teams", help="Favorite sports teams or star")
