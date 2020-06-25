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


class PickupPrice(models.TransientModel):


    """ Pickup Price settings model"""
    _inherit = 'res.config.settings'
    _name = "pickup.price"

    default_distance = fields.Float(
        string="Distance", default_model='pickup.price', default='1')
    default_fixed_distance = fields.Float(
        string="Fixed Distance", default_model='pickup.price', default='10')

    uom_unit = fields.Many2one(comodel_name='product.uom',
                               string='UOM',
                               readonly=False,
                               default_model='pickup.price',
                               )
    default_rate = fields.Float(
        string="Rate", default_model='pickup.price', default='10')
    default_rate_after = fields.Float(
        string="Price per Distance", default_model='pickup.price', default='100')
    default_rate_after_uom = fields.Char(
        string="Unit", related="uom_unit.name",)

    default_department = fields.Many2one(
        comodel_name='hr.department',
        string="Department")

    @api.multi
    def set_default_uom_unit(self):
        IrValues = self.env['ir.default']
        IrValues.set(
            'pickup.price', 'uom_unit', self.uom_unit.id,)

    @api.multi
    def set_default_department_unit(self):
        IrValues = self.env['ir.default']
        IrValues.set(
            'pickup.price', 'default_department', self.default_department.id)
