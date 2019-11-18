# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo.tests


@odoo.tests.common.tagged('at_install', 'post_install')
class TestUi(odoo.tests.HttpCase):

    def test_01_remove_developer_mode_menu_elements(self):
        env = self.env
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        env['ir.module.module'].search([('name', '=', 'web_debranding')], limit=1).state = 'installed'

        url = '/web'
        code = """
                        setInterval(function(){
                            if (!$('header > nav > ul.o_menu_systray > li.o_user_menu > div.dropdown-menu').length) {
                                console.log('page is loading');
                                return;
                            }
                            setTimeout(function(){
                            // request ..../res.users/is_admin may take some time
                            // TODO: add a way to check that it's a time to check result (variable on loading in web_debranding/static/src/js/user_menu.js ?)
                            if ($('a[data-menu="debug"]').length > 0 || $('a[data-menu="debugassets"]').length > 0) {
                                console.log('error', 'Developer mode menu elements are displayed for not admin user');
                            } else {
                                console.log('ok');
                            }
                            })
                        }, 1000);
        """
        self.browser_js(url, code, login="demo", ready='odoo.isReady === true')

    def test_02_remove_developer_mode_menu_elements(self):
        env = self.env
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        env['ir.module.module'].search([('name', '=', 'web_debranding')], limit=1).state = 'installed'

        url = '/web'
        code = """
                        setInterval(function(){
                            if (!$('header > nav > ul.o_menu_systray > li.o_user_menu > div.dropdown-menu').length) {
                                console.log('page is loading');
                                return;
                            }
                            if ($('a[data-menu="debug"]').length > 0 && $('a[data-menu="debugassets"]').length > 0) {
                                console.log('ok');
                            } else {
                                console.log('error', 'Developer mode menu elements are not displayed for admin');
                            }
                        }, 1000);
        """
        self.browser_js(url, code, login="admin", ready='odoo.isReady === true')
