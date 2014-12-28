{
    'name' : 'Quick add items to shopping cart',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://it-projects.info',
    'description': """

Adds

    [-] 0[+]

buttons to the products cell (near the price). When customer click "+" or type count at the input field a product will added immediatly.

and on the product page removes "Add to Cart" button
and add the same buttons to show current count of a products in the cart. When customer click "+" or type count at the input field a product will added immediatly.

TODO don't ignore multivariant products

Tested on Odoo 8.0 f8d5a6727d3e8d428d9bef93da7ba6b11f344284
    """,
    'depends' : ['website_sale'],
    'data':[
        'website_sale_add_to_cart_views.xml',
        ],
    'installable': True
}
