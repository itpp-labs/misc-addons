from openerp.osv import fields, osv


class ir_actions_todo(osv.osv):
    _inherit = 'ir.actions.todo'

    _columns = {
        'repeat': fields.boolean(string='Repeat'),
    }

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
