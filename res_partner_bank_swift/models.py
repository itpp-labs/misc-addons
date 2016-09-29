# -*- coding: utf-8 -*-
from openerp import models, fields


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"


    bank_swift = fields.Char('SWIFT')

