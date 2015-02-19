{
    'name' : 'Simplified website checkout',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://yelizariev.github.io',
    'description': """
Shoper type email address and receive message with sale order id. No payments, no deliveries.

Tested on Odoo 8.0 d023c079ed86468436f25da613bf486a4a17d625
    """,
    'depends' : [
        'website_sale',
    ],
    'data':[
        'website_sale_order_templates.xml',
        ],
    'installable': True
}
