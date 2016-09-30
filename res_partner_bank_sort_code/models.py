# -*- coding: utf-8 -*-
from openerp import models, fields


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"


    sort_code = fields.Char('Sort code')

