# -*- coding: utf-8 -*-
from openerp.osv import osv, fields


class ResPartnerBank(osv.osv):
    _inherit = "res.partner.bank"

    _columns = {
        'sort_code': fields.char('Sort code'),
    }
