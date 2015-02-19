{
    'name' : 'Product status at website shop',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://yelizariev.github.io',
    'description': """
Adds "New" Ribbon (like "Sale").

Adds automatic ribbons:

* DISCONTINUED --  stock is 0 and the status is End of Life or Obsolete.
* BACKORDERED -- stock is 0 and the status is Normal,

Puts ribbons text at the product page.

Disables "Add to cart" future if product is discontinued.

Tested on Odoo 8.0 f8d5a6727d3e8d428d9bef93da7ba6b11f344284.
    """,
    'depends' : ['website_sale', 'stock'],
    'data':[
        'website_sale_stock_status_views.xml',
        'website_sale_stock_status_data.xml',
        ],
    'installable': True
}
