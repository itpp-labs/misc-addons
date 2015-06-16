from openerp import api, models, SUPERUSER_ID
from openerp.osv import osv, fields


class ir_actions_act_window_debranding(models.Model):
    _inherit = 'ir.actions.act_window'
    ir_config_parameter_name_key = 'web_debranding.new_name'

    def _get_new_name(self, cr, uid, ids, context=None):
        model = self.pool.get('ir.config_parameter')
        ids = model.search(
            cr, uid,
            [('key', '=', self.ir_config_parameter_name_key)], context=context)
        records = model.browse(cr, uid, ids, context=context)
        return records[0].value

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        """ call the method get_empty_list_help of the model and set the window action help message
        """
        new_name = self._get_new_name(cr, uid, ids, context)
        new_name = new_name.strip()
        if new_name == '':
            new_name = 'Software'
        ids_int = isinstance(ids, (int, long))
        if ids_int:
            ids = [ids]
        results = super(ir_actions_act_window_debranding, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        if not fields or 'help' in fields:
            for res in results:
                model = res.get('res_model')
                if model and self.pool.get(model):
                    ctx = dict(context or {})
                    tmp = self.pool[model].get_empty_list_help(cr, uid, res.get('help', ""), context=ctx)
                    if (tmp):
                        tmp = tmp.replace('Odoo', new_name)
                    res['help'] = tmp
        if ids_int:
            return results[0]
        return results
