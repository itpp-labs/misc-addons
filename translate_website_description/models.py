# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    website_description = fields.Html('Description for the website', translate=True)



class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    website_description = fields.Text('Description for the website', translate=True)



class WebsiteResPartner(models.Model):
    _inherit = 'res.partner'

    website_description = fields.Html(
            'Website Partner Full Description',
            translate=True,
    )



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    website_description = fields.Html('Line Description', translate=True)



class SaleOrderOption(models.Model):
    _inherit = "sale.order.option"

    website_description = fields.Html('Line Description', translate=True)



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    website_description = fields.Html('Description', translate=True)

