from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    salesperson_sale_order_ids = fields.One2many('sale.order', 'user_id', 'Salesperson Sales Order')
