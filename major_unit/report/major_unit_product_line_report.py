from odoo import models, tools, api, fields
import odoo.addons.decimal_precision as dp


class MajorUnitProductReport(models.Model):
    _name = "report.major_unit.product_line"
    _description = "Parts and Labor of Major Unit"
    _auto = False

    major_unit_id = fields.Many2one('major_unit.major_unit', string='Major Unit', readonly=True)
    product_id = fields.Many2one('product.product', string='Parts', readonly=True)

    price_unit = fields.Float('Price', compute='_compute_price')
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), readonly=True)

    discount = fields.Float('Discount', compute='_compute_discount', readonly=True)
    # currency_id = fields.Many2one(related='major_unit_id.currency_id', store=True, string='Currency', readonly=True)

    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)], compute='_compute_tax_id')
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', readonly=True)
    price_tax = fields.Float(compute='_compute_amount', string='Taxes', readonly=True)
    price_total = fields.Float(compute='_compute_amount', string='Total', readonly=True)

    # @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            partner = None
            currency = None
            taxes = line.tax_id.compute_all(price, currency, line.product_uom_qty, product=line.product_id, partner=partner)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.multi
    def _compute_price(self):
        for r in self:
            r.price_unit = r.product_id.lst_price

    @api.multi
    def _compute_discount(self):
        for r in self:
            r.discount = 0

    @api.multi
    def _compute_tax_id(self):
        for r in self:
            r.tax_id = self.env['account.tax']

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_major_unit_product_line')
        self._cr.execute("""
            CREATE VIEW report_major_unit_product_line AS (
            SELECT
                ro_product.product_id as id,
                ro_product.product_id as product_id,
                ro.major_unit_id as major_unit_id,
                SUM(ro_product.quantity) as product_uom_qty
            FROM
                service_repair_order_product as ro_product
            LEFT JOIN
                service_repair_order as ro ON ro.id = ro_product.repair_order_id
            GROUP BY
                product_id,
                major_unit_id
        )
        """)
