# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID

class ir_attachment(osv.Model):
    _inherit = 'ir.attachment'

    _columns = {
        'res_model_tmp': fields.char('Resource Model (TMP)', readonly=True, help="The database object this attachment will be attached to"),
        'res_id_tmp': fields.integer('Resource ID (TMP)', readonly=True, help="The record id this is attached to"),
    }

class account_analytic_account(osv.Model):
    _inherit = 'account.analytic.account'
    _columns = {
        'user_id_tmp': fields.many2one('res.users', 'Case manager (TMP)'),
    }
