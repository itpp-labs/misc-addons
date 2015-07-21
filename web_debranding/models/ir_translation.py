import re
import inspect
import types

import openerp
from openerp import SUPERUSER_ID, models, tools, api


class ir_translation(models.Model):
    _inherit = 'ir.translation'

    def _debrand(self, cr, uid, source):
        if not source or not re.search(r'\bodoo\b', source, re.IGNORECASE):
            return source

        new_name = self.pool['ir.config_parameter'].get_param(cr, SUPERUSER_ID, 'web_debranding.new_name', False)

        if not new_name:
            return source

        return re.sub(r'\bodoo\b', new_name, source, re.IGNORECASE)

    @tools.ormcache(skiparg=3)
    def _get_source(self, cr, uid, name, types, lang, source=None, res_id=None):
        res = super(ir_translation, self)._get_source(cr, uid, name, types, lang, source, res_id)
        return self._debrand(cr, uid, res)
