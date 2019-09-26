from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"
    customer_owned = fields.Boolean(string="Customer Owned")
    loaner1 = fields.Boolean(string="Is a Loaner Bike")

    @api.onchange('loaner1')
    def loaner_bike(self):
        if self.loaner1 == True:
            self.sale_ok = False
            self.purchase_ok = False
            self.customer_owned = False

    @api.onchange('customer_owned')
    def customer_bike(self):
        if self.customer_owned == True:
            self.sale_ok = False
            self.purchase_ok = False
            self.loaner1 = False


class CustomerOwned(models.Model):
    _inherit = 'major_unit.major_unit'

    @api.onchange('prod_lot_id')
    def change_form_status(self):
        if self.prod_lot_id.product_id.customer_owned:
            self.form = 'customer_owned'
