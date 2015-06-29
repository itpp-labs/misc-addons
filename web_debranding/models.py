from openerp import api, models, fields, SUPERUSER_ID
from openerp.tools.translate import _

class ir_actions_act_window_debranding(models.Model):
    _inherit = 'ir.actions.act_window'

    def read(self, cr, uid, ids, fields=None,
             context=None, load='_classic_read'):
        results = super(ir_actions_act_window_debranding, self).read(
            cr, uid, ids, fields=fields, context=context, load=load)
        if not fields or 'help' in fields:
            new_name = self.pool.get('ir.config_parameter').get_param(
                cr, uid, 'web_debranding.new_name', False, context)
            new_name = new_name and new_name.strip() or  _('Software')
            for res in results:
                if type(res) is dict and res.get('help'):
                    res['help'] = res['help'].replace('Odoo', new_name)
        return results
