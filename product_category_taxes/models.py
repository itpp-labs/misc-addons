from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_new_taxes(self, categ_id):
        new_category = self.env['product.category'].browse(categ_id)
        new_taxes = {
            'taxes_id': [(6, 0, new_category.taxes_id.ids)],
            'supplier_taxes_id': [(6, 0, new_category.supplier_taxes_id.ids)]
        }
        return new_taxes

    @api.onchange('categ_id')
    def _update_product_category_taxes(self):
        if self.categ_id:
            new_taxes = self._get_new_taxes(self.categ_id.id)
            self.taxes_id = new_taxes['taxes_id']
            self.supplier_taxes_id = new_taxes['supplier_taxes_id']

    @api.model
    def create(self, vals):
        if vals.get('categ_id'):
            new_taxes = self._get_new_taxes(vals['categ_id'])
            vals.update(new_taxes)
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('categ_id'):
            new_taxes = self._get_new_taxes(vals['categ_id'])
            vals.update(new_taxes)
        return super(ProductTemplate, self).write(vals)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    taxes_id = fields.Many2many(
        'account.tax', 'product_category_taxes_rel', 'category_id', 'tax_id', string="Customer Taxes",
        domain=[('type_tax_use', '!=', 'purchase')],
        help="This taxes will be copied to the product customer taxes."
    )
    supplier_taxes_id = fields.Many2many(
        'account.tax', 'product_category_supplier_taxes_id', 'category_id', 'tax_id', string="Vendor Taxes",
        domain=[('type_tax_use', '!=', 'sale')],
        help="This taxes will be copied to the product vendor taxes."
    )
