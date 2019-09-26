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
import datetime


class ProductCategoryFront(models.Model):

    """ Models for woocommerce product category """
    _name = 'product.category.front'

    name = fields.Char('Name')
    slug = fields.Char('Slug')
    parent = fields.Many2one(comodel_name='product.category.front',
                             string='Parent Category',
                             help='Parent Category')


class ProductDetails(models.Model):
    _name = "product.vehicle.details"

    model_code = fields.Char(string='Model Code',
                             help='Vehicle model code')
    video = fields.Binary(string='Video',
                          help='Video of vehicle')
    incentives = fields.Char(string='Incentives',
                             help='Manufacturers')
    msrp = fields.Char(string='MSRP',
                       help='Manufacturer’s suggested Retail Price')
    invoice = fields.Float(string='Invoice',
                           help='Actual invoice cost from the manufacturer')
    delivery = fields.Float(string='Delivery',
                            help='Delivery charge from manufacturer')
    punched = fields.Boolean(string='Punched',
                             help='Has the bike been registered as sold with manufacturer ')
    claims = fields.Float(string='Claims',
                          help='MV? Claimed Incentives booked to A/R')
    condition = fields.Selection([('available', 'Available'),
                                  ('used', 'Used')],
                                 string='Condition',
                                 help='Product condition')
    option = fields.Text(string='Vehicle Specifications',
                         help='Additional technical informations/options of the vehicle.')

    setup_charges = fields.Float(string='Setup Charges')
    freight_charges = fields.Float(string='Freight Charges')
    documents_fees = fields.Float(string=' Document Fees')
    job_code = fields.Char(string="Job Code")
    hours = fields.Float(string="Hours")
    job_description = fields.Char(string="Job Description")
    charge_by = fields.Char(string="Charged By")
    labor_rate = fields.Float(string="Labor Rate")


class Products(models.Model):

    """Custom fields for Products"""
    _name = 'product.template'
    _inherit = ['product.template', 'base_details', 'product.vehicle.details']

    def _model_selection(self):
        selection = super(Products, self)._model_selection()
        return selection

    review_type_id = fields.Many2many('product.review', string="Review Type", domain="[('product_type', '=', details_model)]")

    @api.model
    def create(self, vals):
        template = super(Products, self).create(vals)
        if 'review_type_id' in vals:
            ids=[]
            for re in vals['review_type_id']:
                if 'rating' in re[2]:
                    if re[2]['rating'] > 5:
                        raise Warning('Product review should be less than 5.')
            for i in vals['review_type_id']:
                if i != False:
                    review_id=self.env['product.review'].search([('id','=',i[1])])
                    ids.append(review_id)
            template.update({'review_type_id':[(6, 0,[y.id for y in ids])]})
        return template

    @api.multi
    def write(self, vals):
        template = super(Products, self).write(vals)
        if 'review_type_id' in vals:
            ids=[]
            for re in vals['review_type_id'][1:]:
                if 'rating' in re[2]:
                    if re[2]['rating'] > 5 :
                        raise Warning('Product review should be less than 5.')
        return template

    @api.multi
    @api.onchange('details_model')
    def on_change_review(self):
        keys =[]
        if self.details_model == 'product.template.details' :
            for key in self.env['product.review'].search([('product_type', '=', 'product.template.details')]):
                if key[0].rating >= 1:
                    key[0].rating = 0
                keys.append(key.id)
        else :
            for key in self.env['product.review'].search([('product_type', '=', self.details_model)]):
                if key[0].rating >= 1:
                    key[0].rating = 0
                keys.append(key.id)
        self.update({'review_type_id':[(6, 0,[y for y in keys])]})

