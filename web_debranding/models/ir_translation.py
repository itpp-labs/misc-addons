# -*- coding: utf-8 -*-
import re

from odoo import api
from odoo import models
from odoo import tools

from .ir_config_parameter import PARAMS


def debrand(env, source):
    if not source or not re.search(r'\bodoo\b', source, re.IGNORECASE):
        return source

    if env:
        params = env['ir.config_parameter'].get_debranding_parameters()
    else:
        # use default values
        params = dict(PARAMS)

    new_name = params.get('web_debranding.new_name')
    new_website = params.get('web_debranding.new_website')

    try:
        source = unicode(source, 'utf-8')
    except:
        pass

    source = re.sub(r'\bodoo.com\b', new_website, source, flags=re.IGNORECASE)

    # We must exclude the case when after the word "odoo" is the word "define".
    # Since JS functions are also contained in the localization files.
    # Example:
    # po file: https://github.com/odoo/odoo/blob/9.0/addons/im_livechat/i18n/ru.po#L853
    # xml file: https://github.com/odoo/odoo/blob/9.0/addons/im_livechat/views/im_livechat_channel_templates.xml#L148
    source = re.sub(r'\bodoo(?!\.define)\b', new_name, source, flags=re.IGNORECASE)
    return source


class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    @api.model
    def _debrand_dict(self, res):
        for k in res:
            res[k] = self._debrand(res[k])
        return res

    @api.model
    def _debrand(self, source):
        return debrand(self.env, source)

    @tools.ormcache('name', 'types', 'lang', 'source', 'res_id')
    def __get_source(self, name, types, lang, source, res_id):
        res = super(IrTranslation, self).__get_source(name, types, lang, source, res_id)
        return self._debrand(res)

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
