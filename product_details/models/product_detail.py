# -*- coding: utf-8 -*-
from odoo import models


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'base_details']
