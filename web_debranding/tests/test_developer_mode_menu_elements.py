# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo.tests
from odoo.api import Environment


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_remove_developer_mode_menu_elements(self):
        env = Environment(self.registry.test_cr, self.uid, {})
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        env['ir.module.module'].search([('name', '=', 'web_debranding')], limit=1).state = 'installed'
        self.registry.cursor().release()

        url = '/web'
        code = """
                    $(document).ready( function() {
                        setInterval(function(){
                            if (!$('.navbar-collapse.collapse .oe_user_menu_placeholder .dropdown-menu').length) {
                                console.log('page is loading');
                                return;
                            }
                            setTimeout(function(){
                            // request ..../res.users/is_admin may take some time
                            // TODO: add a way to check that it's a time to check result (variable on loading in web_debranding/static/src/js/user_menu.js ?)
                            if ($('li a[data-menu="debug"]').length > 0 || $('li a[data-menu="debugassets"]').length > 0) {
                                console.log('error', 'Developer mode menu elements are displayed for non-admin user');
                            } else {
                                console.log('ok');
                            }
                            }, 1000);
                        }, 1000);
                    })
        """
        self.phantom_js(url, code, login="demo")

    def test_02_remove_developer_mode_menu_elements(self):
        env = Environment(self.registry.test_cr, self.uid, {})
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        env['ir.module.module'].search([('name', '=', 'web_debranding')], limit=1).state = 'installed'
        self.registry.cursor().release()

        url = '/web'
        code = """
                    $(document).ready( function() {
                        setInterval(function(){
                            if (!$('.navbar-collapse.collapse .oe_user_menu_placeholder .dropdown-menu').length) {
                                console.log('page is loading');
                                return;
                            }
                            if ($('li a[data-menu="debug"]').length > 0 && $('li a[data-menu="debugassets"]').length > 0) {
                                console.log('ok');
                            } else {
                                console.log('error', 'Developer mode menu elements are not displayed for admin');
                            }
                        }, 1000);
                    })
        """
        self.phantom_js(url, code, login="admin")
