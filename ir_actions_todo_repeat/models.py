from odoo import api, fields, models


class IrActionsTodo(models.Model):
    _inherit = "ir.actions.todo"

    repeat = fields.Boolean(string="Repeat", repeat=False)

    @api.multi
    def action_launch(self, context=None):
        res = super(IrActionsTodo, self).action_launch(context=context)
        for wizard in self:
            if wizard.type in ("automatic", "once") and wizard.repeat:
                wizard.write({"state": "open"})
        return res
