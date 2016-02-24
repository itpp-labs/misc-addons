# -*- coding: utf-8 -*-
from openerp import models, api, tools, SUPERUSER_ID
import re


class Planner(models.Model):
    _inherit = 'web.planner'

    @api.model
    def render(self, template_id, planner_app):
        res = super(Planner, self).render(template_id, planner_app)
        new_company = self.env['ir.config_parameter'].get_debranding_parameters().get('web_debranding.new_name')
        planner_footer = self.env['ir.config_parameter'].get_debranding_parameters().get('web_debranding.planner_footer')
        planner_footer = '<p>' + str(planner_footer) + '</p>'
        res = re.sub(r'<p>[^<]*to contact our accounting experts by using the[\s\S]*?</div>', planner_footer, res)
        res = re.sub(r'<p>[^<]*If you need help, do not hesitate to contact our experts[\s\S]*?</div>', planner_footer, res)
        res = re.sub(r'<h4>Don\'t hesitate to[\s\S]*logo.png"/>', '', res)
        res = re.sub(r'<p>Once it\'s fully working[\s\S]*odoo_logo.png"/>', planner_footer, res)
        res = re.sub(r'<div class="mt32">[\s\S]*Fabien Pinckaers, Founder[\s\S]*?</div>', planner_footer, res)
        res = re.sub(r'[Oo]doo', str(new_company), res)
        return res