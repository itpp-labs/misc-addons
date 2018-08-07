# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests import common, api


class TestUI(common.HttpCase):

    at_install = True
    post_install = True

    def test_ui(self):
        # FIXME: we cannot use demo user to test, because with no other modules
        # installed there is no menu but Website which redirects to homepage

        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        phantom_env = api.Environment(self.registry.test_cr, self.uid, {})
        phantom_env['ir.module.module'].search(
            [('name', '=', 'web_website')], limit=1
        ).state = 'installed'

        menu = self.env.ref('website.menu_website_configuration')
        tour = 'web_website.tour'
        self.phantom_js(
            '/web#menu_id=%i' % menu.id,
            "odoo.__DEBUG__.services['web_tour.tour']"
            ".run('%s')" % tour,

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".tours['%s'].ready" % tour,

            login='admin',
        )
