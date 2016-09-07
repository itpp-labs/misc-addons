# -*- coding: utf-8 -*-
import re

from openerp import SUPERUSER_ID
from openerp import models
from openerp import tools
from openerp.tools.translate import _


class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    def _debrand(self, cr, uid, source):
        if not source or not re.search(r'\bodoo\b', source, re.IGNORECASE):
            return source

        new_name = self.pool['ir.config_parameter'].get_param(cr, SUPERUSER_ID, 'web_debranding.new_name') or _('Software')

        return re.sub(r'\bodoo\b', new_name, source, flags=re.IGNORECASE)

    @tools.ormcache(skiparg=3)
    def _get_source(self, cr, uid, name, types, lang, source=None, res_id=None):
        res = super(IrTranslation, self)._get_source(cr, uid, name, types, lang, source, res_id)
        return self._debrand(cr, uid, res)
