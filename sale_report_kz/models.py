from openerp import fields, models
from openerp.addons.sale_report_ru.models import money_to_words
try:
    from pytils import numeral
except ImportError:
    pass

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    def _get_amount_tax(self):
        cr = self._cr
        uid = self.env.uid
        line = self

        # from addons/sale/sale.py
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)

        self.amount_tax = val

    amount_tax = fields.Float('Amount tax', compute=_get_amount_tax)

class procurement_group(models.Model):
    _inherit = 'procurement.group'

    sale_order_id = fields.Many2one('sale.order', 'Sale order')

class sale_order(models.Model):
    _inherit = 'sale.order'

    def _prepare_procurement_group(self, cr, uid, order, context=None):
        res = super(sale_order, self)._prepare_procurement_group(cr, uid, order, context=None)
        res.update({'sale_order_id': order.id})
        return res

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    def _get_amount_total_in_words(self):
        amount = self.group_id.sale_order_id.amount_total
        code = self.company_id.currency_id.name
        self.amount_total_in_words = money_to_words(amount, code)

    def _get_amount_items_in_words(self):
        amount = len(self.move_lines)
        self.amount_items_in_words = numeral.in_words(int(amount))

    amount_total_in_words = fields.Char('Amount total (in words)', compute=_get_amount_total_in_words)

    amount_items_in_words = fields.Char('Amount items (in words)', compute=_get_amount_items_in_words)
