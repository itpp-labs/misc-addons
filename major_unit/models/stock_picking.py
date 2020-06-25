from odoo import api, models


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_done(self):
        res = super(Picking, self).action_done()
        self._create_major_units_for_picking()
        return res

    def _create_major_units_for_picking(self):
        major_unit = self.env['major_unit.major_unit']
        for pack_op_lot in self.mapped('move_line_ids').mapped('lot_id'):
            if not pack_op_lot.major_unit_ids:
                purchase_order = self.env['purchase.order'].search([('name', '=', self.origin)])[0]
                major_unit.create({
                    'prod_lot_id': pack_op_lot.id,
                    'purchase_order_id': purchase_order.id,
                    'date_received': self.date_done,
                })
