# -*- coding: utf-8 -*-
import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_check_timer(self):
        self.phantom_js(
            '/web',

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".run('project_timelog_tour')",

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".tours.project_timelog_tour.ready",

            login="admin",
        )
