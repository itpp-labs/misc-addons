#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2015 credativ ltd. <info@credativ.co.uk>
#    Copyright (c) 2019 Matteo Bilotta <mbilotta@linkgroup.it>
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
from odoo import _, api, fields, models
from odoo.osv import expression
from odoo.exceptions import ValidationError


class ProductTag(models.Model):
    _name = 'product.tag'
    _description = "Product tags"
    _order = 'name'
    _parent_order = 'name'
    _parent_store = True

    name = fields.Char('Tag Name', required=True, translate=True)
    active = fields.Boolean(help='The active field allows you to hide the tag without removing it.', default=True)
    color = fields.Integer(string="Color index", default=0)
    image = fields.Binary(sintrg="Image")

    parent_id = fields.Many2one(string='Parent Tag', comodel_name='product.tag', index=True, ondelete='cascade')
    child_ids = fields.One2many(string='Child Tags', comodel_name='product.tag', inverse_name='parent_id')
    parent_path = fields.Char(index=True)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_("You cannot create recursive product tags."))

    @api.multi
    def name_get(self):
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
            parent_ids = []
            parent_domain = []

            for tag in map(lambda t: t.strip(), name.split('/')):
                name_domain = expression.AND([[('name', operator, tag)], parent_domain])
                parent_ids = self._search(name_domain, limit=limit, access_rights_uid=name_get_uid)
                parent_domain = [('parent_id', 'in', parent_ids)]

            browse_domain = expression.OR([[('id', 'in', parent_ids)], parent_domain])
            args = expression.AND([browse_domain, args])

        tag_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)

        return self.browse(tag_ids).name_get()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tag_ids = fields.Many2many(string='Tags',
                               comodel_name='product.tag',
                               relation='product_product_tag_rel',
                               column1='tag_id',
                               column2='product_id')
