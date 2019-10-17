import logging

from odoo import models, fields, api, tools
from odoo.addons.base.models.ir_config_parameter import IrConfigParameter as IrConfigParameterOriginal

_logger = logging.getLogger(__name__)

# params that has to be shared across all companies
SHARED_KEYS = [
    'database.expiration_date',
]
FIELD_NAME = 'value'


class IrConfigParameter(models.Model):
    _inherit = ['ir.config_parameter', 'website_dependent.mixin']
    _name = 'ir.config_parameter'

    value = fields.Text(company_dependent=True, website_dependent=True)

    @api.model
    def create(self, vals):
        res = super(IrConfigParameter, self).create(vals)
        # make value company independent
        res._force_default(FIELD_NAME, vals.get('value'))
        return res

    def write(self, vals):
        res = super(IrConfigParameter, self).write(vals)
        value = vals.get('value')
        if value:
            for r in self:
                if r.key in SHARED_KEYS:
                    r._force_default(FIELD_NAME, value)

        if any(k in vals for k in ('key', 'value')):
            self._update_properties_label(FIELD_NAME)

        return res

    @api.model
    def get_param(self, key, default=False):
        if not self.env.context.get('force_company'):
            website_id = self.env.context.get('website_id')
            if website_id:
                website = self.env['website'].browse(website_id)
                company_id = website.company_id.id
            else:
                # Warning. Since odoo 11.0 it means that by default Administrator's company value is used
                company_id = self.env.user.company_id.id
            self = self.with_context(force_company=company_id)

        return super(IrConfigParameter, self).get_param(key, default)

    @api.model
    @tools.ormcache_context('self._uid', 'key', keys=('force_company', 'website_id'))
    def _get_param(self, key):
        _logger.debug('_get_param(%s) context: %s', key, self.env.context)
        # call undecorated super method. See odoo/tools/cache.py::ormcache and http://decorator.readthedocs.io/en/stable/tests.documentation.html#getting-the-source-code
        return IrConfigParameterOriginal._get_param.__wrapped__(self, key)

    def _auto_init(self):
        self._auto_init_website_dependent(FIELD_NAME)
        return super(IrConfigParameter, self)._auto_init()
