# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


GET_CONTEXT = dict(
    _get_domain_website_dependent=True,
    _search_order_website_dependent=True,
    _search_make_website_priority=True,
)


class IrProperty(models.Model):

    _inherit = 'ir.property'

    website_id = fields.Many2one('website', 'Website')

    @api.multi
    def _update_values(self, values):
        """Support for html fields.

        Can be removed in first odoo release with this patch: https://github.com/odoo/odoo/pull/26556
        """
        if values.get('type') == 'html':
            values['type'] = 'text'
        return super(IrProperty, self)._update_values(values)

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
            new_order.insert(0, 'website_id')
            order = ','.join(new_order)
        if self.env.context.get('_search_domain_website_dependent'):
            website_id = self._get_website_id()
            args.append(('website_id', '=', website_id))
        ids = super(IrProperty, self)._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid
        )
        if self.env.context.get('_search_make_website_priority'):
            # built-in get_multi makes priority for records with res_id
            # which breaks case "**Website** is matched, **Resource** is empty"
            # when there is another record with Company and Resource only
            res = self.browse(ids)
            for prop in res:
                if prop.website_id and not prop.res_id:
                    # This value is default for this website.
                    # Exclude all records without website
                    res = res.filtered(lambda r: r.website_id)
                    break
            return res.ids

        return ids

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
            **GET_CONTEXT
        )).get(name, model, res_id=res_id)

    @api.model
    def get_multi(self, name, model, ids):
        return super(IrProperty, self._check_website_dependent(
            name, model,
            **GET_CONTEXT
        )).get_multi(name, model, ids)

    @api.model
    def search_multi(self, name, model, operator, value):
        return super(IrProperty, self._check_website_dependent(
            name, model,
            **GET_CONTEXT
        )).search_multi(name, model, operator, value)

    @api.model
    def set_multi(self, name, model, values, default_value=None):
        return super(IrProperty, self._check_website_dependent(
            name, model,
            _search_domain_website_dependent=True,
            create_website_dependent=True,
        )).set_multi(name, model, values, default_value=default_value)

    @api.multi
    def _update_db_value_website_dependent(self, field):
        """Update db value if it's a default value"""
        for r in self:
            if r.fields_id != field:
                # It's another field
                continue
            if r.company_id:
                # it's not default value
                continue
            # r.website_id is empty here,
            # because otherwise r.company_id is not empty too
            if not r.res_id:
                # It's not record-specific
                continue
            # Default value is updated. Set new value in db column
            model, res_id = r.res_id.split(',')
            value = r.get_by_record()
            model = field.model_id.model
            record = self.env[model].browse(int(res_id))
            record._update_db_value(field, value)
