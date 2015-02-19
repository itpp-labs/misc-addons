{
    'name' : 'Sales team in eCommerce',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://yelizariev.github.io',
    'description': """
Split products by sales team.

Tested on Odoo 8.0 d023c079ed86468436f25da613bf486a4a17d625
    """,
    'depends' : [
        'sales_team',
        'website_sale',
        'website_sale_order',
    ],
    'data':[
        'security/website_sales_team_security.xml',
        'security/ir.model.access.csv',
        'website_sales_team_data.xml',
        'website_sales_team_templates.xml',
        'website_sales_team_views.xml',
        ],
    'installable': True
}
