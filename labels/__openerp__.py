{
    'name' : 'Labels',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category' : 'Custom',
    'website' : 'https://yelizariev.github.io',
    'description': """
Adds templates for printing labels. See module labels_custom for example of usage.

Tested on Odoo 8.0 f8d5a6727d3e8d428d9bef93da7ba6b11f344284
    """,
    'depends' : ['report'],
    'data':[
        'labels_views.xml',
        'labels_templates.xml',
        'labels_data.xml',
        ],
    'installable': True
}
