# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Author: Romain Deheele)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Continent(models.Model):
    _name = 'res.continent'
    _description = 'Continent'
    _order = 'name'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(
        string='Continent Name',
        help='The full name of the continent.',
        required=True, translate=True)
    country_ids = fields.One2many(
        'res.country', 'continent_id', string="Countries")
