# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountChart(models.TransientModel):

    _inherit = 'account.chart'


    company_id = fields.Many2one('res.company')

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id
    }
