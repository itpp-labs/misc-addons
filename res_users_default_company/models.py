# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class res_users(models.Model):
    _inherit = 'res.users'

    company_default_id = fields.Many2one('res.company', string='Default company')
