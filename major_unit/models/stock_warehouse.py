from odoo import api, fields, models


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    wh_major_unit_loc_id = fields.Many2one('stock.location', 'Major Units')

    @api.model
    def create(self, vals):
        warehouse_id = super(Warehouse, self).create(vals)
        warehouse_id._initialize_warehouse()
        return warehouse_id

    @api.multi
    def _initialize_warehouse(self):
        stock_location_obj = self.env['stock.location']
        if not stock_location_obj.search([('name', '=', 'Major Units')]):
            stock_location_obj.create({
                'name': 'Major Units',
                'usage': 'view',
            })

