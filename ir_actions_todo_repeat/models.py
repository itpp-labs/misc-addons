from openerp.osv import fields, osv


class ir_actions_todo(osv.osv):
    _inherit = 'ir.actions.todo'

    _columns = {
        'no_repeat': fields.boolean(string='No Repeat'),
    }

    _defaults = {
        'no_repeat': True,
    }

    def action_launch(self, cr, uid, ids, context=None):
        res = super(ir_actions_todo, self).action_launch(cr, uid, ids, context)
        wizard_id = ids and ids[0] or False
        wizard = self.browse(cr, uid, wizard_id, context=context)
        if wizard.type in ('automatic', 'once') and not wizard.no_repeat:
            wizard.write({'state': 'open'})
        return res
