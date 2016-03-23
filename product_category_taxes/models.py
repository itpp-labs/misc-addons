from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_new_taxes(self, categ_id, old_category=None):
        new_category = self.env['product.category'].browse(categ_id)
        new_taxes = {
            'taxes_id': [(4, new_tax) for new_tax in new_category.taxes_id.ids],
            'supplier_taxes_id': [(4, new_tax) for new_tax in new_category.supplier_taxes_id.ids]
        }
        if old_category:
            new_taxes['taxes_id'] += [(3, old_tax) for old_tax in old_category.taxes_id.ids]
            new_taxes['supplier_taxes_id'] += [(3, old_tax) for old_tax in old_category.supplier_taxes_id.ids]
        return new_taxes

    @api.model
    def create(self, vals):
        if vals.get('categ_id'):
            new_taxes = self._get_new_taxes(vals['categ_id'])
            vals['taxes_id'] += new_taxes['taxes_id']
            vals['supplier_taxes_id'] += new_taxes['supplier_taxes_id']
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('categ_id'):
            new_taxes = self._get_new_taxes(vals['categ_id'], self.categ_id)
            vals.update(new_taxes)
        return super(ProductTemplate, self).write(vals)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    taxes_id = fields.Many2many(
        'account.tax', 'product_category_taxes_rel', 'category_id', 'tax_id', string="Customer Taxes",
        domain=[('type_tax_use', '!=', 'purchase')],
        help="When you set the product category for your product, these taxes will be copied to the product customer taxes."
    )
    supplier_taxes_id = fields.Many2many(
        'account.tax', 'product_category_supplier_taxes_id', 'category_id', 'tax_id', string="Vendor Taxes",
        domain=[('type_tax_use', '!=', 'sale')],
        help="When you set the product category for your product, these taxes will be copied to the product vendor taxes."
    )
