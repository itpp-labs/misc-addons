from openerp import fields, models


class ir_actions_todo(models.Model):
    _inherit = 'ir.actions.todo'


    repeat = fields.Boolean(string='Repeat')


    _defaults = {
        'repeat': False,
    }

    def action_launch(self, cr, uid, ids, context=None):
        res = super(ir_actions_todo, self).action_launch(cr, uid, ids, context)
        wizard_id = ids and ids[0] or False
        wizard = self.browse(cr, uid, wizard_id, context=context)
        if wizard.type in ('automatic', 'once') and wizard.repeat:
            wizard.write({'state': 'open'})
        return res
