# -*- coding: utf-8 -*-
from openerp.tests import HttpCase

@openerp.tests.common.at_install(True)
@openerp.tests.common.post_install(True)
class TestUi(HttpCase):

    def test_01_check_timer(self):
        self.phantom_js("/", "odoo.__DEBUG__.services['web.Tour'].run('project_timelog', 'test')", "odoo.__DEBUG__.services['web.Tour'].tours.project_timelog", login="admin")
