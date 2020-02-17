# Copyright 2019 Anvar Kildebekov <https://it-projects.info/team/fedoranvar>
# License MIT (https://opensource.org/licenses/MIT).

import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):
    def main(self):

        env = self.env
        wrong_text = "<script><p></p></script>" "<p></p>" '<img src="link">'
        correct_text = "<p></p>" '<img src="link">'
        test_text = "<p>Check. mate</p>"
        demo_user = env["res.users"].search([("login", "=", "demo")])
        admin_user = env["res.users"].search([("login", "=", "admin")])
        env["res.users.signature"].create(
            {
                "name": "test1",
                "template": wrong_text,
                "user_ids": [(6, 0, [demo_user.id, admin_user.id])],
            }
        )
        for i in [demo_user, admin_user]:
            self.assertEqual(i.signature, correct_text)
        temp_signature = env["res.users.signature"].create(
            {"name": "test2", "template": test_text}
        )
        admin_user.write({"signature_id": temp_signature.id})
        self.assertEqual(admin_user.signature, test_text)

    def test_01_res_users_signature(self):
        self.main()
