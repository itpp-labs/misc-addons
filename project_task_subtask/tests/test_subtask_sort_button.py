# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):
    def test_01_subtask_sort_button(self):
        self.env["ir.module.module"].search(
            [("name", "=", "project_task_subtask")], limit=1
        ).state = "installed"
        self.start_tour("/web", "task_subtask", login="admin")
