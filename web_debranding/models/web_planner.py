# -*- coding: utf-8 -*-
from openerp import models, api, tools, SUPERUSER_ID


class Planner(models.Model):
    _inherit = 'web.planner'

    @api.model
    def render(self, template_id, planner_app):
        res = super(Planner, self).render(template_id, planner_app)
        new_company = self.env['ir.config_parameter'].get_debranding_parameters().get('web_debranding.new_name')
        new_person = self.env['ir.config_parameter'].get_debranding_parameters().get('web_debranding.new_person')
        replace_dict = {
            '<p>Enjoy your Software experience,</p>': '',
            '<img class="signature mb8" src="/web_planner/static/src/img/fabien_signature.png"/>': '',
            'For the Software Team': 'Best Regards',
            'Fabien Pinckaers, Founder': str(new_person),
            'Odoo': str(new_company),
            'odoo': str(new_company),
        }
        for old_text, new_text in replace_dict.iteritems():
            res = res.replace(old_text, new_text)
        return res