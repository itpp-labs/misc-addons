# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp import SUPERUSER_ID


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'


    res_model_tmp = fields.Char('Resource Model (TMP)', readonly=True, help="The database object this attachment will be attached to")
    res_id_tmp = fields.Integer('Resource ID (TMP)', readonly=True, help="The record id this is attached to")



class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    user_id_tmp = fields.Many2one('res.users', 'Case manager (TMP)')

