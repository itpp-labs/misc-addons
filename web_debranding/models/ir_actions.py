# -*- coding: utf-8 -*-
from openerp import models
from openerp.tools.translate import _


class IrActionsActWindowDebranding(models.Model):
    _inherit = 'ir.actions.act_window'

    def read(self, cr, uid, ids, fields=None,
             context=None, load='_classic_read'):
        results = super(IrActionsActWindowDebranding, self).read(
            cr, uid, ids, fields=fields, context=context, load=load)
        if not fields or 'help' in fields:
            params = self.pool.get('ir.config_parameter').get_debranding_parameters(cr, uid, context)
            new_name = params.get('web_debranding.new_name')
            for res in results:
                if isinstance(res, dict) and res.get('help'):
                    res['help'] = res['help'].replace('Odoo', new_name)
        return results
