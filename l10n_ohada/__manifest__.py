# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (c) 2018 ERGOBIT Consulting - www.ergobit.org
# contact: info@ergobit.org

{
    'name': 'OHADA - Accounting',
    'category': 'Localization',
    'author' : 'ERGOBIT', 
    'description': """
Accounting Chart for OHADA
================================

This module implements the accounting chart for OHADA countries.

Countries that belong to OHADA are the following:
--------------------------------------------------
    Benin, Burkina Faso, Cameroon, Central African Republic, Comoros, Congo,
    Ivory Coast, Gabon, Guinea, Guinea Bissau, Equatorial Guinea, Mali, Niger,
    Replica of Democratic Congo, Senegal, Chad, Togo.
    
    """,
    'depends' : [
        'account', 
        'base_vat', 
    ],
    'data': [
        # 'data/res.country.group.csv',
        # 'data/account.group.csv',
        # 'data/account_chart_template_data_1.xml',
        # 'data/account.account.template.csv',
        # 'data/account_chart_template_data_2.xml',
        # 'data/account_tax_data.xml',
        # 'data/account_tax_template_data.xml',
        # 'data/account_brs_template_data.xml',
        # 'data/fiscal_position_template_data.xml',
        # 'data/account_chart_load_template.xml',
        #
        # 'views/account_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    #'licence': 'OPL-1',
}
