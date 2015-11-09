{
    'name' : 'Link Repair orders & phonecalls',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category' : 'Custom',
    'website' : 'https://yelizariev.github.io',
    'description': """

* Adds field "Repair Order" to phonecall
* Adds smart button "Phonecalls" to Repair Order form.

Tested on Odoo 8.0 ea60fed97af1c139e4647890bf8f68224ea1665b
    """,
    'depends' : ['crm', 'mrp_repair'],
    'data':[
        'views.xml',
        ],
    'installable': True
}
