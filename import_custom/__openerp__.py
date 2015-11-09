{
    'name' : 'Custom import module',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category' : 'Tools',
    'website' : 'https://yelizariev.github.io',
    'description': """
    Prepare some data for import
    """,
    "external_dependencies": {
        'python': ['MySQLdb', 'pandas']
    },
    'depends' : ['import_framework', 'product', 'contacts', 'website_sale'],
    'data':[
        'wizard/upload.xml',
        #'data.xml',
        ],
    'installable': True,
    'auto_install': False,
}
