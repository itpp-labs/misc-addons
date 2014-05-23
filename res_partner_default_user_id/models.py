# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID

class res_partner(osv.Model):
    _inherit = 'res.partner'

    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
    }
    
