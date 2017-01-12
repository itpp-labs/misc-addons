# -*- coding: utf-8 -*-
from odoo import models


class ProductTemplate(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'base_details']
