# Copyright 2016-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016 Stanislav Krotov <https://it-projects.info/team/ufaks>
# Copyright 2017 Ilmir Karamov <https://it-projects.info/team/ilmir-k>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2018 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2018 WohthaN <https://github.com/WohthaN>
# License MIT (https://opensource.org/licenses/MIT).

import re

from odoo import api, models

from .ir_translation import debrand_bytes


class Planner(models.Model):
    _inherit = "web.planner"

    @api.model
    def render(self, template_id, planner_app):
        res = super(Planner, self).render(template_id, planner_app)
        params = self.env["ir.config_parameter"].get_debranding_parameters()
        planner_footer = params.get("web_debranding.planner_footer")
        planner_footer = "<p>" + planner_footer + "</p>"
        planner_footer = bytes(planner_footer, "utf-8")

        res = re.sub(
            rb"<p>[^<]*to contact our accounting experts by using the[\s\S]*?</div>",
            planner_footer,
            res,
        )
        res = re.sub(
            rb"<p>[^<]*If you need help, do not hesitate to contact our experts[\s\S]*?</div>",
            planner_footer,
            res,
        )
        res = re.sub(rb'<h4>Don\'t hesitate to[\s\S]*logo.png"/>', b"", res)
        res = re.sub(
            rb'<p>Once it\'s fully working[\s\S]*odoo_logo.png"/>', planner_footer, res
        )
        res = re.sub(
            rb'<div class="mt32">[\s\S\n]*Fabien Pinckaers, Founder[\s\S\n]*?</div>',
            planner_footer,
            res,
        )
        res = re.sub(
            rb"<div[^<]*<strong>See it in action [\s\S]*?</strong><br/>[\s\S]*?<iframe[^<]*www.youtube.com/embed/204DbheXfWw[\s\S]*?</iframe>[^<]*</div>",
            b"",
            res,
        )
        res = re.sub(
            rb'<img src="/web_planner/static/src/img/odoo_logo.png"/>', b"", res
        )
        return debrand_bytes(self.env, res)
