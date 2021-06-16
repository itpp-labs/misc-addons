# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from . import models


def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # emulate updating existing field to website-dependent one
    env.cr.execute("ALTER TABLE test_website_dependent ADD COLUMN foo VARCHAR")
    env.cr.execute("ALTER TABLE test_website_dependent ADD COLUMN user_id INTEGER")


def post_load():
    from . import api
