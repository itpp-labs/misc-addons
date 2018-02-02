# -*- coding: utf-8 -*-
import re

from odoo import models, api

from .ir_translation import debrand_bytes


class Planner(models.Model):
    _inherit = 'web.planner'

    @api.model
    def render(self, template_id, planner_app):
        res = super(Planner, self).render(template_id, planner_app)
        params = self.env['ir.config_parameter'].get_debranding_parameters()
        planner_footer = params.get('web_debranding.planner_footer')
        planner_footer = '<p>' + planner_footer + '</p>'
        planner_footer = bytes(planner_footer, 'utf-8')

        res = re.sub(rb'<p>[^<]*to contact our accounting experts by using the[\s\S]*?</div>', planner_footer, res)
        res = re.sub(rb'<p>[^<]*If you need help, do not hesitate to contact our experts[\s\S]*?</div>', planner_footer, res)
        res = re.sub(rb'<h4>Don\'t hesitate to[\s\S]*logo.png"/>', b'', res)
        res = re.sub(rb'<p>Once it\'s fully working[\s\S]*odoo_logo.png"/>', planner_footer, res)
        res = re.sub(rb'<div class="mt32">[\s\S\n]*Fabien Pinckaers, Founder[\s\S\n]*?</div>', planner_footer, res)
        res = re.sub(rb'<div[^<]*<strong>See it in action [\s\S]*?</strong><br/>[\s\S]*?<iframe[^<]*www.youtube.com/embed/204DbheXfWw[\s\S]*?</iframe>[^<]*</div>', '', res)
        res = re.sub(rb'<img src="/web_planner/static/src/img/odoo_logo.png"/>', '', res)
        return debrand_bytes(self.env, res)
