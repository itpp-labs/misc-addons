# Copyright 2018,2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        res = super(Http, self).session_info()
        user = request.env.user
        display_switch_website_menu = (
            user.has_group("web_website.group_multi_website")
            and len(user.backend_website_ids) > 1
        )
        if display_switch_website_menu:
            current_website = user.backend_website_id or user.backend_website_ids[0]

            res["user_websites"] = {
                "current_website": (current_website.id, current_website.name),
                "allowed_websites": [(w.id, w.name) for w in user.backend_website_ids],
            }
        res["display_switch_website_menu"] = display_switch_website_menu
        return res

    @classmethod
    def _add_dispatch_parameters(cls, func):
        super(Http, cls)._add_dispatch_parameters(func)

        context = {}
        context["allowed_website_ids"] = request.website.ids

        # modify bound context
        request.context = dict(request.context, **context)

        if request.routing_iteration == 1:
            request.website = request.website.with_context(request.context)
