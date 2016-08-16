# -*- coding: utf-8 -*-
from openerp.osv import osv, fields


class product_template(osv.Model):
    _inherit = 'product.template'
    _columns = {
        'website_description': fields.html('Description for the website', translate=True),
    }


class delivery_carrier(osv.Model):
    _inherit = 'delivery.carrier'
    _columns = {
        'website_description': fields.text('Description for the website', translate=True),
    }


class WebsiteResPartner(osv.Model):
    _inherit = 'res.partner'
    _columns = {
        'website_description': fields.html(
            'Website Partner Full Description',
            translate=True,
        ),
    }


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
        'website_description': fields.html('Line Description', translate=True),
    }


class sale_order_option(osv.osv):
    _inherit = "sale.order.option"
    _columns = {
        'website_description': fields.html('Line Description', translate=True),
    }


class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'website_description': fields.html('Description', translate=True),
    }
