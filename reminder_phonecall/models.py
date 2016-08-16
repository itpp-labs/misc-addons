# -*- coding: utf-8 -*-
from openerp import models


class crm_phonecall(models.Model):
    _name = 'crm.phonecall'
    _inherit = ['crm.phonecall', 'reminder']
