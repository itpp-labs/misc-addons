# -*- coding: utf-8 -*-
import re

from openerp import api
from openerp import models
from openerp import tools


class IrTranslation(models.Model):
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
        Example:
        po file: https://github.com/odoo/odoo/blob/9.0/addons/im_livechat/i18n/ru.po#L853
        xml file: https://github.com/odoo/odoo/blob/9.0/addons/im_livechat/views/im_livechat_channel_templates.xml#L148
        """
        return re.sub(r'\bodoo(?!\.define)\b', new_name, source, flags=re.IGNORECASE)

    @tools.ormcache('name', 'types', 'lang', 'source', 'res_id')
    def __get_source(self, cr, uid, name, types, lang, source, res_id):
        res = super(IrTranslation, self).__get_source(cr, uid, name, types, lang, source, res_id)
        return self._debrand(cr, uid, res)

    @api.model
    @tools.ormcache_context('model_name', keys=('lang',))
    def get_field_string(self, model_name):
        res = super(IrTranslation, self).get_field_string(model_name)
        return self._debrand_dict(res)

    @api.model
    @tools.ormcache_context('model_name', keys=('lang',))
    def get_field_help(self, model_name):
        res = super(IrTranslation, self).get_field_help(model_name)
        return self._debrand_dict(res)
