# -*- coding: utf-8 -*-

from openerp import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'
    vk =  fields.Char(string="VK", size=64)

