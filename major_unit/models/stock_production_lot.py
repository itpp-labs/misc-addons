from odoo import api, models, fields
from lxml import etree


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    major_unit_ids = fields.One2many('major_unit.major_unit', 'prod_lot_id')
    sale_order_line_ids = fields.One2many(
        'sale.order.line', 'lot_id', 'Sale Order Lines', copy=False,
        help='Technical field. Used for store a value of a major unit "state" field.')

    @api.multi
    @api.depends('name', 'product_id', 'product_id.name')
    def name_get(self):
        return [(lot.id, "%s: %s" % (lot.product_id.name, lot.name)) for lot in self]

    def get_current_location(self):
        """
        A returned value is correct for production lot with one quant only
        """
        stock_move = self.env['stock.move'].search([
            ('quant_ids', 'in', self.quant_ids.ids), ('state', '=', 'done')], order='id DESC', limit=1)
        if not stock_move:
            return None
        return stock_move.location_dest_id

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ProductionLot, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        from_mu = self._context.get('creation_from_major_unit')
        if from_mu:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='product_id']"):
                node.set('domain', "[('details_model', '=', 'vehicle')]")
            res['arch'] = etree.tostring(doc)
        return res
