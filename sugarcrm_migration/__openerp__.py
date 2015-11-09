{
    'name' : 'import SugarCRM + kashflow data to odoo ',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category' : 'Tools',
    'website' : 'https://yelizariev.github.io',
    'description': """
Depends on:

* http://pandas.pydata.org/
* http://mysql-python.sourceforge.net/MySQLdb.html

Odoo optimisation:

* modify openerp/addons/base/res/res_partner.py in order to skip calling function _fields_sync (via checking context.get('skip_addr_sync'))
* remove website module in order to optimise importing data in ir.attachment table

    """,
    "external_dependencies": {
        'python': ['MySQLdb', 'pandas']
    },
    'depends' : ['import_framework', 'crm', 'project', 'sale_mediation_custom', 'multi_company'],
    'data':[
        'wizard/upload.xml',
        'data.xml',
        ],
    'installable': True,
    'auto_install': False,
}
