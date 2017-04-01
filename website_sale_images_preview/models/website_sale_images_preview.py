# -*- coding: utf-8 -*-
from odoo import models


class ProductImage(models.Model):
    _name = 'product.image'
    _inherit = ['product.image', 'web.preview']

    _preview_media_file = 'image'
