{
    'name' : 'Autopay in eCommerce',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Custom',
    'website' : 'https://yelizariev.github.io',
    'description': """
After customer make an online payment (e.g. via paypal), new invoice is created and validated.

Tested on Odoo 8.0 f8d5a6727d3e8d428d9bef93da7ba6b11f344284
    """,
    'depends' : ['website_sale', 'payment'],
    'data':[
        'website_sale_autopay_views.xml',
        ],
    'installable': True
}
