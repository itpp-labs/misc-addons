{
    'name' : 'Sales team in eCommerce (custom)',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://yelizariev.github.io',
    'description': """

Tested on Odoo 8.0 d023c079ed86468436f25da613bf486a4a17d625
    """,
    'depends' : [
        'res_users_clear_access_rights',
        'website_sales_team',
        'website_sale_add_to_cart',
        'website_sale_clear_cart',
        'portal',
    ],
    'data':[
        'website_sales_team_custom_views.xml',
        ],
    'installable': True
}
