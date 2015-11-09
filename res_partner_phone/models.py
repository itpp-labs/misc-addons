# -*- coding: utf-8 -*-
from openerp import models
from openerp.osv import fields


class ResPartnerPhone(models.Model):
    _inherit = 'res.partner'

    _display_name_store_triggers = {
        'res.partner': (lambda self, cr, uid, ids, context=None: self.search(cr, uid,
                        [('id', 'child_of', ids)], context=dict(active_test=False)),
                        ['parent_id', 'is_company', 'name', 'mobile', 'phone'], 10)
        }

    _display_name = lambda self, *args, **kwargs: self._display_name_compute(*args, **kwargs)
    _columns = {
        'display_name': fields.function(_display_name, type='char', string='Name',
                                        store=_display_name_store_triggers, select=True)
        }

    def name_get(self, cr, uid, ids, context=None):
        result = dict(super(ResPartnerPhone, self).name_get(cr, uid, ids, context=None))
        records = self.browse(cr, uid, result.keys(), context)
        for r in records:
            if r.mobile:
                result[r.id] = result[r.id] + ' (' + r.mobile + ')'
            if r.phone:
                result[r.id] = result[r.id] + ' (' + r.phone + ')'
        return result.items()
