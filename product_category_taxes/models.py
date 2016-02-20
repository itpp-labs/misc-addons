from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('categ_id')
    def _update_product_category_taxes(self):
        if self.categ_id:
            new_category = self.env['product.category'].browse(self.categ_id.id)
            self.taxes_id = [(6, 0, new_category.taxes_id.ids)]
            self.supplier_taxes_id = [(6, 0, new_category.supplier_taxes_id.ids)]

    @api.multi
    def write(self, vals):
        if vals.get('categ_id'):
            new_category = self.env['product.category'].browse(vals['categ_id'])
            vals.update({
                'taxes_id': [(6, 0, new_category.taxes_id.ids)],
                'supplier_taxes_id': [(6, 0, new_category.supplier_taxes_id.ids)],
            })
        return super(ProductTemplate, self).write(vals)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    taxes_id = fields.Many2many(
        'account.tax', 'product_category_taxes_rel', 'category_id', 'tax_id', string="Customer Taxes",
        domain=[('type_tax_use', '!=', 'purchase')])
    supplier_taxes_id = fields.Many2many(
        'account.tax', 'product_category_supplier_taxes_id', 'category_id', 'tax_id', string="Vendor Taxes",
        domain=[('type_tax_use', '!=', 'sale')]
    )
