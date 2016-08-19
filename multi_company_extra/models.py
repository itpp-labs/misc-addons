# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
import werkzeug.utils
import openerp
from openerp.addons.base.ir import ir_qweb


class account_chart(osv.osv_memory):

    _inherit = 'account.chart'

    _columns = {
        'company_id': fields.many2one('res.company')
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id
    }
