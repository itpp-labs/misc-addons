# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2015 credativ ltd. <info@credativ.co.uk>
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
from openerp import api
from openerp import fields
from openerp import models


class ProductTag(models.Model):
    _description = 'Product Tags'
    _name = "product.tag"

    # this should be the default according to the documentation, but no such
    # thing is done in the actual implementation
    _rec_name = 'display_name'

    name = fields.Char('Tag Name', required=True, translate=True)
    display_name = fields.Char('Full Name', compute='_compute_display_name')
    active = fields.Boolean(help='The active field allows you to hide the tag without removing it.', default=True)
    parent_id = fields.Many2one(string='Parent Tag', comodel_name='product.tag', select=True, ondelete='cascade')
    child_ids = fields.One2many(string='Child Tags', comodel_name='product.tag', inverse_name='parent_id')
    parent_left = fields.Integer('Left Parent', select=True)
    parent_right = fields.Integer('Right Parent', select=True)

    image = fields.Binary('Image')

    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

    @api.one
    @api.depends('name', 'parent_id.name')
    def _compute_display_name(self):
        """ Return the tags' display name, including their direct parent. """
        if self.parent_id:
            self.display_name = self.parent_id.display_name + ' / ' + self.name
        else:
            self.display_name = self.name

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        tags = self.search(args, limit=limit)
        return tags.name_get()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tag_ids = fields.Many2many(string='Tags',
                               comodel_name='product.tag',
                               relation='product_product_tag_rel',
                               column1='tag_id',
                               column2='product_id')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
