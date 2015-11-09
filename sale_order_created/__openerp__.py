{
    'name' : 'Notification for new sale order (quotation)',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category' : 'Custom',
    'website' : 'https://yelizariev.github.io',
    'description': """
In the main, module is used to get notification about new quotations in ecommerce. To subscribe to new sale order (i.e. quotation), open related sales team (e.g. Website sales team) and add followers.

Tested on Odoo 8.0 f8d5a6727d3e8d428d9bef93da7ba6b11f344284
    """,
    'depends' : ['sale'],
    'data':[
        'data.xml',
        ],
    'installable': True
}
