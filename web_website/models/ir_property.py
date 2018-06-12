# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class IrProperty(models.Model):

    _inherit = 'ir.property'

    website_id = fields.Many2one('website', 'Website')

    @api.model
    def _is_website_dependent(self, name, model):
        return getattr(self.env[model]._fields[name], 'website_dependent', None)

    @api.model
    def _check_website_dependent(self, name, model, **kwargs):
        if self._is_website_dependent(name, model):
            return self.with_context(website_dependent=True, **kwargs)
        else:
            none_values = dict((key, None) for key in kwargs.keys())
            return self.with_context(**none_values)

    @api.model
    def _get_website_id(self):
        website_id = self._context.get('website_id') or self.env.user.backend_website_id.id
        return website_id

    def _get_domain(self, prop_name, model):
        domain = super(IrProperty, self)._get_domain(prop_name, model)
        if self.env.context.get('_get_domain_website_dependent'):
            website_id = self._get_website_id()
            domain += [('website_id', 'in', [website_id, False])]
        return domain

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self.env.context.get('_search_order_website_dependent'):
            new_order = [order] if order else []
            new_order.append('website_id')
            order = ','.join(new_order)
        if self.env.context.get('_search_domain_website_dependent'):
            website_id = self._get_website_id()
            args.append(('website_id', '=', website_id))
        return super(IrProperty, self)._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid
        )

    @api.model
    def create(self, vals):
        if self.env.context.get('create_website_dependent'):
            website_id = self._get_website_id()
            vals['website_id'] = website_id
        return super(IrProperty, self).create(vals)

    @api.model
    def get(self, name, model, res_id=False):
        return super(IrProperty, self._check_website_dependent(
            name, model,
            _get_domain_website_dependent=True,
            _search_order_website_dependent=True
        )).get(name, model, res_id=res_id)

    @api.model
    def get_multi(self, name, model, ids):
        return super(IrProperty, self._check_website_dependent(
            name, model,
            _get_domain_website_dependent=True,
            _search_order_website_dependent=True
        )).get_multi(name, model, ids)

    @api.model
    def set_multi(self, name, model, values, default_value=None):
        return super(IrProperty, self._check_website_dependent(
            name, model,
            _search_domain_website_dependent=True,
            create_website_dependent=True,
        )).set_multi(name, model, values, default_value=default_value)

    @api.model
    def search_multi(self, name, model, operator, value):
        return super(IrProperty, self._check_website_dependent(
            name, model,
            _search_order_website_dependent=True,
            _get_domain_website_dependent=True,
        )).get(name, model, operator, value)
