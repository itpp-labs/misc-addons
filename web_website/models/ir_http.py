# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(Http, self).session_info()
        user = request.env.user
        display_switch_website_menu = user.has_group('web_website.group_multi_website') and len(user.backend_website_ids) > 1
        res['user_websites'] = {
            'current_website': (
                user.backend_website_id.id,
                user.backend_website_id.name
            ) if user.backend_website_id else False,
            'allowed_websites': [
                (w.id, w.name)
                for w in user.backend_website_ids
            ]
        } if display_switch_website_menu else False

        return res
