# -*- coding: utf-8 -*-
from openerp.osv import osv


class mrp_repair(osv.osv):
    _inherit = 'mrp.repair'

    _defaults = {
        'name': lambda obj, cr, uid, context: '/',
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'mrp.repair') or '/'
        return super(mrp_repair, self).create(cr, uid, vals, context=context)
