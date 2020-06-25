#    Techspawn Solutions Pvt. Ltd.
#    Copyright (C) 2016-TODAY Techspawn(<http://www.Techspawn.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import logging
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class Customers(models.Model):

    """Custom fields for Customers"""

    _inherit = 'res.partner'

    birthdate = fields.Date(string='Birthdate')
    helmet = fields.Char(string="Helmet")
    jacket = fields.Char(string="Jacket")
    pants = fields.Char(string="Pants")
    gloves = fields.Char(string="Gloves")
    boots = fields.Char(string="Boots")

    family = fields.Char(string='Family',
                         help="notes on family members – wife and kids ")
    occupation = fields.Char(string='Occupation',
                             help="what do they do for a living")
    recreation = fields.Char(string='Recreation',
                             help="list of things they enjoy doing")
    motivation = fields.Char(string='Motivation',
                             help="What do they like about stuff/mktg")
    animals = fields.Char(string='Animals',
                          help="place to note any pets")
    teams = fields.Char(string='Teams',
                        help="Favorite sports teams or star")
    licence_no = fields.Char(string='Licence Number',
                             help='Licence Number')
    customer_vehicles = fields.One2many(
        comodel_name='major_unit.major_unit',
        string='Customer Vehicles',
        inverse_name='partner_id',
        readonly=False,
        required=False,
    )

    wishlist_ids = fields.Many2many(
        comodel_name='product.template',
        string='Wishlist',
        readonly=False,
        required=False,
    )
    rewards = fields.Char(string="Rewards")
