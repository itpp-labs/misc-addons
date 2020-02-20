# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl.html).

import odoo.tests


@odoo.tests.at_install(True)
@odoo.tests.post_install(True)
class TestPrintBadge(odoo.tests.HttpCase):
    def test_print_badge(self):
        self.authenticate("admin", "admin")

        demo_user = self.env["res.users"].search([("login", "=", "demo")])
        self.assertEqual(len(demo_user), 1)

        r = self.url_open(
            "/report/html/base_attendance.print_partner_badge/{}".format(demo_user.id)
        )
        self.assertEqual(r.status_code, 200)
