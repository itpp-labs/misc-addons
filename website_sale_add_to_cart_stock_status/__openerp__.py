{
    'name' : 'Quick add items to shopping cart + stock status',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://yelizariev.github.io',
    'description': """

Hide quick add to cart buttons at /shop directory from discontinued products

Tested on Odoo 8.0 f8d5a6727d3e8d428d9bef93da7ba6b11f344284
    """,
    'depends' : ['website_sale_add_to_cart', 'website_sale_stock_status'],
    'data':[
        'views.xml',
        ],
    'installable': True,
    'auto_install': True,
}
