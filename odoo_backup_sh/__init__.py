# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from . import controllers
from . import models
from odoo import api, SUPERUSER_ID


def uninstall_hook(cr, registry):
    # The "odoo_backup_sh.config.cron" inherits from "ir.cron", which inherits from "ir.action.server", which as field
    # model_id with option ondelete='cascade'. During uninstallation model is removed, so odoo tries to delete
    # corresponding ir.action.server records which which raise violations error, because those records are used
    # in "ir.cron" records. So, we need to delete "odoo_backup_sh.config.cron manually
    env = api.Environment(cr, SUPERUSER_ID, {})
    backup_crons = env["odoo_backup_sh.config.cron"].search(
        [("model_name", "=", "odoo_backup_sh.config")]
    )
    if backup_crons:
        backup_crons.unlink()
