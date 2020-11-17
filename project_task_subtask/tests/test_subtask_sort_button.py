# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2020 Almas Giniatullin <https://github.com/almas50>
# License MIT (https://opensource.org/licenses/MIT).

import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):
    def test_01_subtask_sort_button(self):
        self.env["ir.module.module"].search(
            [("name", "=", "project_task_subtask")], limit=1
        ).state = "installed"
        # find active tasks
        task = self.env["project.task"].search([("active", "=", "true")], limit=1)
        url = "/web?#id=%s&view_type=form&model=project.task&/" % str(task.id)
        code = """
            $(document).ready( function() {
                setInterval(function(){
                    if ($('.o_x2m_control_panel .o_cp_buttons .btn.o_pager_sort').length > 0) {
                        console.log('ok');
                    }
                }, 1000);
                setTimeout(function(){
                    if ($('.o_x2m_control_panel .o_cp_buttons .btn.o_pager_sort').length > 0) {
                        console.log('ok');
                    } else {
                        console.log(document.documentElement.innerHTML);
                        console.log('error', 'Sort Button is not displayed');
                    }
                }, 20000);
            });
        """
        self.phantom_js(url, code, login="admin")
