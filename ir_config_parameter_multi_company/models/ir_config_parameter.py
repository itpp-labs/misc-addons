# -*- coding: utf-8 -*-
import logging
import sys

from odoo import models, fields, api, _, tools
from odoo.addons.base.ir.ir_config_parameter import IrConfigParameter as IrConfigParameterOriginal

_logger = logging.getLogger(__name__)
PROP_NAME =_('Default value for "%s"')


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    value = fields.Text(company_dependent=True)

    def create(self, vals):
        res = super(IrConfigParameter, self).create(vals)
        # make value company independent
        domain = self.env['ir.property']._get_domain('value', self._name)
        domain += [('res_id', '=', '%s,%s' % (self._name, res.id))]
        prop = self.env['ir.property'].search(domain)
        prop.company_id = None
        prop.name = PROP_NAME % res.key
        return res


    @api.model
    def get_param(self, key, default=False):
        company_id = self.env.context.get('company_id')
        if not company_id:
            website_id = self.env.context.get('company_id')
            if website_id:
                website = self.env['website'].browse(website_id)
                company_id = website_id.company_id and website_id.company_id.id

        if not company_id:
            company_id = self.env.user.company_id.id

        return super(IrConfigParameter, self.with_context(force_company=company_id)).get_param(key, default)

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
        self.env['ir.property'].create({
            'fields_id': self.env.ref('base.field_ir_config_parameter_value').id,
            'res_id': 'ir.config_parameter,%s' % self.id,
            'name': PROP_NAME % self.key,
            'value': value,
            'type': 'text',
        })

    def _auto_init(self):
        # Check that we have an value column
        cr = self.env.cr
        cr.execute("select COUNT(*) from information_schema.columns where table_name='ir_config_parameter' AND column_name='value';")
        res = cr.dictfetchone()
        if res.get('count'):
            _logger.info('Starting conversion for ir.config_parameter: saving data for further processing.')
            # Rename image column so we don't lose images upon module install
            cr.execute("ALTER TABLE ir_config_parameter RENAME COLUMN value TO value_old")
        else:
            _logger.debug('No value field found in ir_config_parameter; no data to save.')
        return super(IrConfigParameter, self)._auto_init()

    def _auto_end(self):
        super(IrConfigParameter, self)._auto_end()
        cr = self.env.cr
        # Only proceed if we have the appropriate _old field
        cr.execute("select COUNT(*) from information_schema.columns where table_name='ir_config_parameter' AND column_name='value_old';")
        res = cr.dictfetchone()
        if not res.get('count'):
            _logger.debug('No value_old field present in ir_config_parameter; assuming data is already saved in the filestore.')
            return

        _logger.info('Starting rewrite of ir.config_parameter, saving values to ir.property.')
        for r in self.env['ir.config_parameter'].sudo().search([]):
            cr.execute("SELECT key,value_old FROM ir_config_parameter WHERE id = %s", (r.id, ))
            res = cr.dictfetchone()
            key = res.get('key')
            value_old = res.get('value_old')
            r._create_default_value(value_old)
        # Finally, remove the _old column if all went well so we won't run this every time we upgrade the module.
        cr.execute("ALTER TABLE ir_config_parameter DROP COLUMN value_old")
