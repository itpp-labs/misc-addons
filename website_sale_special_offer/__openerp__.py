{
    'name' : 'Special offer in eCommerce',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://it-projects.info',
    'description': """
Module allows to create special offer on a web shop.

Tested on Odoo 8.0 f8d5a6727d3e8d428d9bef93da7ba6b11f344284.
    """,
    'depends' : ['website_sale'],
    'data':[
        'website_sale_special_offer_views.xml',
        ],
    'installable': True
}
