import re
import inspect
import types

import openerp
from openerp import SUPERUSER_ID, models, tools, api


class ir_translation(models.Model):
    _inherit = 'ir.translation'

    def _debrand_dict(self, res):
        for k in res:
            res[k] = self._debrand(res[k])
        return res

    def _debrand(self, cr, uid, source):
        if not source or not re.search(r'\bodoo\b', source, re.IGNORECASE):
            return source

        new_name = self.pool['ir.config_parameter'].get_debranding_parameters(cr, uid).get('web_debranding.new_name')

        if not new_name:
            return source

        """
        We must exclude the case when after the word "odoo" is the word "define".
        Since JS functions are also contained in the localization files.
        """
        return re.sub(r'\bodoo(?!\.define)\b', new_name, source, flags=re.IGNORECASE)

    @tools.ormcache('name', 'types', 'lang', 'source', 'res_id')
    def __get_source(self, cr, uid, name, types, lang, source, res_id):
        res = super(ir_translation, self).__get_source(cr, uid, name, types, lang, source, res_id)
        return self._debrand(cr, uid, res)

    @api.model
    @tools.ormcache_context('model_name', keys=('lang',))
    def get_field_string(self, model_name):
        res = super(ir_translation, self).get_field_string(model_name)
        return self._debrand_dict(res)

    @api.model
    @tools.ormcache_context('model_name', keys=('lang',))
    def get_field_help(self, model_name):
        res = super(ir_translation, self).get_field_help(model_name)
        return self._debrand_dict(res)
