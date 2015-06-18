from openerp import api, models, fields, SUPERUSER_ID


class ir_actions_act_window_debranding(models.Model):
    _inherit = 'ir.actions.act_window'

    def read(self, cr, uid, ids, fields=None,
             context=None, load='_classic_read'):
        results = super(ir_actions_act_window_debranding, self).read(
            cr, uid, ids, fields=fields, context=context, load=load)
        if not fields or 'help' in fields:
            tmp_name = self.pool.get('ir.config_parameter').get_param(
                cr, uid, 'web_debranding.new_name', False, context).strip()
            new_name = tmp_name == '' and 'Software' or tmp_name
            for res in results:
                if type(res) is dict and res.get('help'):
                    res['help'] = res['help'].replace('Odoo', new_name)
        return results
