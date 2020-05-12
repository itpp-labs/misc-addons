# -*- coding: utf-8 -*-
# © 2014-NOW ERGOBIT Consulting (http://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'OHADA Company',
    'summary': 'Company information according to OHADA regulation',
    'version': '12.0',
    'category': 'Localization',
    'author': 'ERGOBIT Consulting',
    'website': 'http://www.ergobit.org',
    'license': 'AGPL-3',
    'sequence': 2,
    'depends': [
#        'ergobase',
        'base_continent',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/company.sector.csv',
        'data/company.activity.csv',
        'data/legal_form.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
    ],
    'installable': True,
    'auto_install': False,      #True,
    'application': False,
}


