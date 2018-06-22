import logging

from odoo import models, fields, api, _, tools
from odoo.addons.base.ir.ir_config_parameter import IrConfigParameter as IrConfigParameterOriginal, _default_parameters

_logger = logging.getLogger(__name__)
PROP_NAME = _('Default value for "%s"')

DATABASE_SECRET_KEY = 'database.secret'

# params that has to be shared across all companies
SHARED_KEYS = [
    'database.expiration_date',
]


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    value = fields.Text(company_dependent=True)

    @api.multi
    def _get_property(self, for_default=False):
        self.ensure_one()

        domain = self.env['ir.property']._get_domain('value', self._name)
        domain += [('res_id', '=', '%s,%s' % (self._name, self.id))]
        if for_default:
            # find: ('company_id', 'in', [company_id, False])
            # update to: ('company_id', 'in', [False])
            domain = [
                ('company_id', 'in', [False])
                if x[0] == 'company_id'
                else
                x
                for x in domain
            ]

        prop = self.env['ir.property'].search(domain)
        return prop

    @api.model
    def create(self, vals):
        res = super(IrConfigParameter, self).create(vals)
        # make value company independent
        res._force_default(vals.get('value'))
        return res

    @api.multi
    def write(self, vals):
        res = super(IrConfigParameter, self).write(vals)
        value = vals.get('value')
        if value:
            for r in self:
                if r.key in SHARED_KEYS:
                    r._force_default(value)
        return res

    def _force_default(self, value):
        """Remove company-dependent values and keeps only default one"""
        self.ensure_one()
        Prop = self.env['ir.property']
        domain = Prop._get_domain('value', self._name)

        # find all props
        props = Prop.search(domain + [
            ('res_id', '=', '%s,%s' % (self._name, self.id)),
        ])

        default_prop = None
        if len(props) == 0:
            default_prop = self._create_default_value(value)
        elif len(props) == 1:
            default_prop = props
        else:
            default_prop = props.filtered(lambda r: not r.company_id)[:1]
            if not default_prop:
                default_prop = props[0]

            # remove rest properties
            (props - default_prop).unlink()

        vals = {
            'name': PROP_NAME % self.key
        }
        if default_prop.company_id:
            vals['company_id'] = None

        if default_prop.get_by_record() != value:
            vals['value'] = value

        default_prop.write(vals)
        self._update_db_value(value)
        return self

    @api.multi
    def write(self, vals):
        res = super(IrConfigParameter, self).write(vals)
        if 'key' in vals:
            # Change property name after renaming the parameter to avoid confusions
            self.ensure_one()  # it's not possible to update key on multiple records
            name = PROP_NAME % vals.get('key')
            prop = self._get_property(for_default=True)
            prop.name = name
        return res

    def _update_db_value(self, value):
        """Store value in db column. We can use it only directly,
        because ORM treat value as computed multi-company field"""
        self.ensure_one()
        self.env.cr.execute("UPDATE ir_config_parameter SET value=%s WHERE id = %s", (value, self.id, ))

    @api.model
    def reset_database_secret(self):
        value = _default_parameters[DATABASE_SECRET_KEY]()
        self.set_param(DATABASE_SECRET_KEY, value)
        return value

    @api.model
    def get_param(self, key, default=False):
        company_id = self.env.context.get('company_id')
        if not company_id:
            website_id = self.env.context.get('website_id')
            if website_id:
                website = self.env['website'].browse(website_id)
                company_id = website.company_id and website.company_id.id

        if not company_id:
            # Warning. Since odoo 11.0 it means that by default Administrator's company value is used
            company_id = self.env.user.company_id.id

        self_company = self.with_context(force_company=company_id)
        res = super(IrConfigParameter, self_company).get_param(key, default)
        if key == DATABASE_SECRET_KEY and not res:
            # If we have empty database.secret, we reset it automatically
            # otherwise admin cannot even login

            # TODO: we don't really need to reset database.secret, because in current version of the module column value is presented and up-to-date. Keep it until we are sure, that without this redefinition everything works after migration from previous versions fo the module.

            return self_company.reset_database_secret()

        return res

    @api.model
    @tools.ormcache_context('self._uid', 'key', keys=("force_company",))
    def _get_param(self, key):
        _logger.debug('_get_param(%s) context: %s', key, self.env.context)
        # call undecorated super method. See odoo/tools/cache.py::ormcache and http://decorator.readthedocs.io/en/stable/tests.documentation.html#getting-the-source-code
        return IrConfigParameterOriginal._get_param.__wrapped__(self, key)

    @api.multi
    def _create_default_value(self, value):
        """Set company-independent default value"""
        self.ensure_one()
        domain = [
            ('company_id', '=', False),
            ('res_id', '=', '%s,%s' % (self._name, self.id))
        ]

        existing = self.env['ir.property'].search(domain)
        if existing:
            # already exists
            return existing

        _logger.debug('Create default value for %s', self.key)
        return self.env['ir.property'].create({
            'fields_id': self.env.ref('base.field_ir_config_parameter_value').id,
            'res_id': '%s,%s' % (self._name, self.id),
            'name': PROP_NAME % self.key,
            'value': value,
            'type': 'text',
        })

    def _auto_init(self):
        cr = self.env.cr
        # rename "value" to "value_tmp"
        # to don't lose values, because during installation the column "value" is deleted
        cr.execute("ALTER TABLE ir_config_parameter RENAME COLUMN value TO value_tmp")

        def post_init_callback():
            self._post_init()
        self.pool.post_init(post_init_callback)
        return super(IrConfigParameter, self)._auto_init()

    def _post_init(self):
        cr = self.env.cr

        # rename "value_tmp" back to "value_tmp"
        cr.execute("ALTER TABLE ir_config_parameter RENAME COLUMN value_tmp TO value")

        for r in self.env['ir.config_parameter'].sudo().search([]):
            cr.execute("SELECT key,value FROM ir_config_parameter WHERE id = %s", (r.id, ))
            res = cr.dictfetchone()
            value = res.get('value')
            # value may be empty after migration from previous module version
            if value:
                # create default value if it doesn't exist
                r._create_default_value(value)
