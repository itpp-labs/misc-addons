{
    'name' : 'import SugarCRM + kashflow data to odoo ',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Base',
    'website' : 'https://it-projects.info',
    'description': """
Depends on:

* http://pandas.pydata.org/
* http://mysql-python.sourceforge.net/MySQLdb.html
    """,
    'depends' : ['crm', 'project', 'sale_mediation_custom', 'multi_company'],
    'data':[
        'wizard/upload.xml',
        'data.xml',
        ],
    'installable': True,
    'auto_install': False,
}
