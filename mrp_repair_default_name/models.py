# -*- coding: utf-8 -*-
from openerp.osv import osv


class MrpRepair(osv.osv):
    _inherit = 'mrp.repair'

    _defaults = {
        'name': lambda obj, cr, uid, context: '/',
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'mrp.repair') or '/'
        return super(MrpRepair, self).create(cr, uid, vals, context=context)
