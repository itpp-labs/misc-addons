from openerp import fields, models, api


class ir_actions_todo(models.Model):
    _inherit = 'ir.actions.todo'

    repeat = fields.Boolean(string='Repeat', repeat=False)

    @api.multi
    def action_launch(self, context=None):
        res = super(ir_actions_todo, self).action_launch(context=context)
        for wizard in self:
            if wizard.type in ('automatic', 'once') and wizard.repeat:
                wizard.write({'state': 'open'})
        return res
