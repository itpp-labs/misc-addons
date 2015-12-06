{
    'name': 'Custom security groups 2',
    'version': '1.0.0',
    'author': 'Cesar Lage',
    'license': 'LGPL-3',
    'category': 'Tools',
    'website': 'https://yelizariev.github.io',
    'description': """
            Custom security groups 2
    """,
    'depends': ['access_base', 'sale', 'crm', 'stock', 'point_of_sale', 'group_menu_no_access'],
    'data': [
        'views.xml',
        'security.xml',
        #'ir.model.access.csv',
        ],
    'installable': True
}
