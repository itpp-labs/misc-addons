# -*- coding: utf-8 -*-
from odoo import models, api


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'base_details']
