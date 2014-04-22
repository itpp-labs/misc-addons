# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
import openerp

class res_partner(osv.Model):
    _inherit = 'res.partner'

    _columns = {
        'skype':fields.char('Skype', size=128, select=True)
    }
