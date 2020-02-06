from . import models


def uninstall_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # remove properties
    field_id = env.ref("base.field_ir_config_parameter_value").id
    env["ir.property"].search([("fields_id", "=", field_id)]).unlink()
