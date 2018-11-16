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
from odoo import _
from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError


class ProductTag(models.Model):
    _description = 'Product Tags'
    _name = "product.tag"
    _order = 'name'
    _parent_order = 'name'
    _parent_store = True

    name = fields.Char('Tag Name', required=True, translate=True)
    active = fields.Boolean(help='The active field allows you to hide the tag without removing it.', default=True)
    parent_id = fields.Many2one(string='Parent Tag', comodel_name='product.tag', index=True, ondelete='cascade')
    child_ids = fields.One2many(string='Child Tags', comodel_name='product.tag', inverse_name='parent_id')
    parent_path = fields.Char(index=True)
    image = fields.Binary('Image')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive tags.'))

    @api.multi
    def name_get(self):
        """ Return the tags' display name, including their direct parent. """
        res = []
        for category in self:
            names = []
            current = category
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((category.id, ' / '.join(reversed(names))))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        partner_category_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(partner_category_ids).name_get()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tag_ids = fields.Many2many(string='Tags',
                               comodel_name='product.tag',
                               relation='product_product_tag_rel',
                               column1='tag_id',
                               column2='product_id')
