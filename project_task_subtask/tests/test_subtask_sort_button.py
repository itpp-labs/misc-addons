# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo.tests
from odoo.api import Environment


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_subtask_sort_button(self):
        env = Environment(self.registry.test_cr, self.uid, {})
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        env['ir.module.module'].search([('name', '=', 'project_task_subtask')], limit=1).state = 'installed'
        # find active tasks
        task = env['project.task'].search([('active', '=', 'true')], limit=1)
        url = '/web?#id=%s&view_type=form&model=project.task&/' % str(task.id)
        self.registry.cursor().release()

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
