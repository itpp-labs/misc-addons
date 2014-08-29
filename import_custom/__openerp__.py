{
    'name' : 'Custom import module',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Base',
    'website' : 'https://it-projects.info',
    'description': """
    Prepare some data for import
    """,
    'depends' : ['import_framework', 'product', 'contacts', 'website_sale'],
    'data':[
        'wizard/upload.xml',
        #'data.xml',
        ],
    'installable': True,
    'auto_install': False,
}
