#-*- coding:utf-8 -*-
from odoo import fields, models


class HrCategoryCommission(models.Model):
    _name = 'hr.category_commission'
    _description = 'Commission For Vehicle Category'

    category_id = fields.Many2one(
        'product.attribute.value', string='Vehicle Category',
        domain=lambda self: [
            ('attribute_id', '=', self.env.ref('drm_product_attributes.product_attribute_category_name').id)
        ])
    commission = fields.Float(string='Commission (%)')

    _sql_constraints = [
        ('category_id_uniq', 'unique (category_id)', "There is already a commission for this vehicle category!"),
    ]


class HrMUSpecialCommission(models.Model):
    _name = 'hr.mu_special_commission'
    _description = 'Commission For Special Major Unit'

    major_unit_id = fields.Many2one('major_unit.major_unit', string='Major Unit')
    commission = fields.Float(string='Commission (%)')

    _sql_constraints = [
        ('major_unit_id_uniq', 'unique (major_unit_id)', "There is already a commission for this major unit!"),
    ]
