# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging
from odoo import models, fields, api
from odoo.addons.base.res.ir_property import TYPE2FIELD


_logger = logging.getLogger(__name__)

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
        # Due to https://github.com/odoo/odoo/commit/b6d32de31e0e18a506ae06dc27561d1d078f3ab1 commit
        # We override the super method to make it website dependent
        # It has the same idea and structure, but sql request and set record value method are changed
        if not ids:
            return {}
        # it's important, that website_id cannot be False -- otherwise, an error is raised on SQL request
        website_id = self._get_website_id() or None
        field = self.env[model]._fields[name]
        field_id = self.env['ir.model.fields']._get(model, name).id
        company_id = self._context.get('force_company') or self.env['res.company']._company_default_get(model, field_id).id or None

        if field.type == 'many2one':
            comodel = self.env[field.comodel_name]
            model_pos = len(model) + 2
            value_pos = len(comodel._name) + 2
            query = """
                SELECT substr(p.res_id, %s)::integer, r.id, p.company_id, p.website_id
                FROM ir_property p
                LEFT JOIN {} r ON substr(p.value_reference, %s)::integer=r.id
                WHERE p.fields_id=%s
                    AND (p.company_id=%s OR p.company_id IS NULL)
                    AND (p.website_id=%s OR p.website_id IS NULL)
                    AND (p.res_id IN %s OR p.res_id IS NULL)
                ORDER BY p.website_id NULLS FIRST, p.company_id NULLS FIRST
            """.format(comodel._table)
            params = [model_pos, value_pos, field_id, company_id, website_id]
        elif field.type in TYPE2FIELD:
            model_pos = len(model) + 2
            query = """
                SELECT substr(p.res_id, %s)::integer, p.{0}, p.company_id, p.website_id
                FROM ir_property p
                WHERE p.fields_id=%s
                    AND (p.company_id=%s OR p.company_id IS NULL)
                    AND (p.website_id=%s OR p.website_id IS NULL)
                    AND (p.res_id IN %s OR p.res_id IS NULL)
                ORDER BY p.website_id NULLS FIRST, p.company_id NULLS FIRST
            """.format(TYPE2FIELD[field.type])
            params = [model_pos, field_id, company_id, website_id]
        else:
            return dict.fromkeys(ids, False)

        # retrieve values
        cr = self.env.cr
        result = {}
        refs = {"%s,%s" % (model, id) for id in ids}
        for sub_refs in cr.split_for_in_conditions(refs):
            cr.execute(query, params + [sub_refs])
            fetched_result = cr.fetchall()
            _logger.debug('Properties for website=%s, company=%s, resource=%s:\n%s', website_id, company_id, sub_refs, fetched_result)
            # fetched_result format: [(res_id, val, company_id, website_id), ...]
            # fetched_result sorting:

            # [(RES_ID, 'only_res', None, None),
            # (None, 'only_field', None, None),

            # (RES_ID, 'company_and_resource', COMPANY, None),
            # (None, 'only_company', COMPANY, None),

            # (RES_ID, 'website_and_resource', None, WEBSITE),
            # (None, 'only_website', None, WEBSITE),

            # (RES_ID, 'company_website', COMPANY, WEBSITE)]

            res = {
                i[0]: i for i in fetched_result
            }
            result.update(res)

        # result format: {res_id: (res_id, val, company_id, website_id), ...}
        # from fetched result was taken only the last row for each res_id

        # Take value for None key, i.e.
        # {{None: (None, val0, company_id0, website_id0), ...}, res_id1: (res_id1, val1, company_id1, website_id1), ...}
        # when there is no such key, use value None
        default_value = result.pop(None, None)
        default_company_id = default_value and default_value[2]
        default_website_id = default_value and default_value[3]
        for id in ids:
            if id not in result:
                # 5 Company, Resource and Website are empty (i.e. only Field is matched)
                result[id] = default_value
            else:
                result_website_id = result[id][3]
                if result_website_id:
                    # 1 Website and Resource are matched
                    continue
                if default_website_id:
                    # 2 Website is matched, Resource is empty
                    result[id] = default_value
                # No properties with website
                result_company_id = result[id][2]
                if result_company_id:
                    # 3 Company and Resource are matched, Website is empty
                    continue
                # no property for res and company
                if default_company_id:
                    # 4 Company is matched, Resource and Website are empty
                    result[id] = default_value

        for key, value in result.items():
            # set data to appropriate form
            result[key] = value and value[1]
        # result format: {id: val, ...}
        return result

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
