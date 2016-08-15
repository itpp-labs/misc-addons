# -*- coding: utf-8 -*-
from openerp.osv import osv, fields


class res_partner_bank(osv.osv):
    _inherit = "res.partner.bank"

    _columns = {
        'bank_swift': fields.char('SWIFT'),
    }
