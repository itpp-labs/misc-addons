# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api
import logging


_logger = logging.getLogger(__name__)


class WebsiteDependentMixin(models.AbstractModel):
    """Mixin Class with helpers to convert previously normal fields to website-depedent"""

    _name = 'website_dependent.mixin'

    def _prop_label(self, field_name, company=None, website=None):
        self.ensure_one()
        label = self.display_name
        label = "%s: %s's " % (field_name, label)
        if not company and not website:
            label += 'default'
        elif website:
            label += 'company + website'
        else:
            label += 'company'
        return label

    def _update_properties_label(self, field_name):
        for r in self:
            domain = self.env['ir.property']._get_domain(field_name, self._name)
            domain += [('res_id', '=', '%s,%s' % (self._name, self.id))]
            for prop in self.env['ir.property'].search(domain):
                prop.name = self._prop_label(field_name, prop.company_id, prop.website_id)

    def _force_default(self, field_name, prop_value):
        """Remove company-dependent values and keeps only default one"""
        self.ensure_one()
        Prop = self.env['ir.property']
        domain = Prop._get_domain(field_name, self._name)

        # find all props
        props = Prop.search(domain + [
            ('res_id', '=', '%s,%s' % (self._name, self.id)),
        ])

        field = self._get_field_object(field_name)

        default_prop = None
        if len(props) == 0:
            default_prop = self._create_default_value(field, prop_value)
        elif len(props) == 1:
            default_prop = props
        else:
            default_prop = props.filtered(lambda r: not r.company_id)[:1]
            if not default_prop:
                default_prop = props[0]

            # remove rest properties
            (props - default_prop).unlink()

        vals = {
            'name': self._prop_label(field_name),
        }
        if default_prop.company_id:
            vals['company_id'] = None

        value = default_prop.get_by_record()
        try:
            # many2one field is an object here
            value = value.id
        except AttributeError:
            pass
        try:
            prop_value = prop_value.id
        except AttributeError:
            pass
        if value != prop_value:
            vals['value'] = prop_value

        default_prop.write(vals)
        self._update_db_value(field, prop_value)
        return self

    def _update_db_value(self, field, value):
        """Store value in db column. We can use it only directly,
        because ORM treat value as computed multi-company field"""
        self.ensure_one()
        try:
            # many2one field might be an object here
            value = value.id
        except AttributeError:
            pass

        if not value:
            if field.ttype == 'boolean':
                value = False
            else:
                value = None

        self.env.cr.execute("UPDATE %s SET %s=%%s WHERE id = %s" % (self._table, field.name, self.id), (value,))

    @api.multi
    def _create_default_value(self, field, prop_value):
        """Set company-independent default value"""
        self.ensure_one()
        domain = [
            ('company_id', '=', False),
            ('fields_id', '=', field.id),
            ('res_id', '=', '%s,%s' % (self._name, self.id))
        ]

        existing = self.env['ir.property'].search(domain)
        if existing:
            # already exists
            return existing

        label = self._prop_label(field.name)
        return self.env['ir.property'].create({
            'fields_id': field.id,
            'res_id': '%s,%s' % (self._name, self.id),
            'name': label,
            'value': prop_value,
            'type': field.ttype,
        })

    def _get_field_object(self, field_name):
        return self.env['ir.model.fields'].search([
            ('name', '=', field_name),
            ('model_id.model', '=', self._name)
        ])

    def _auto_init_website_dependent(self, field_name):
        cr = self.env.cr
        # rename FIELD to "FIELD_tmp"
        # to don't lose values, because during installation the column "value" is deleted
        cr.execute("ALTER TABLE %s RENAME COLUMN %s TO %s_tmp" % (self._table, field_name, field_name))

        self.pool.post_init(self._post_init_website_dependent, field_name)

    def _post_init_website_dependent(self, field_name):
        cr = self.env.cr

        # rename "FIELD_tmp" back to "FIELD"
        cr.execute("ALTER TABLE %s RENAME COLUMN %s_tmp TO %s" % (self._table, field_name, field_name))

        field = self._get_field_object(field_name)
        for r in self.sudo().search([]):
            cr.execute("SELECT %s FROM %s WHERE id = %s" % (field_name, self._table, r.id))
            res = cr.dictfetchone()
            value = res.get(field_name)
            # value may be empty after migration from previous module version
            if value:
                # create default value if it doesn't exist
                r._create_default_value(field, value)
