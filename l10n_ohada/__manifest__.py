# -*- coding: utf-8 -*-
# Copyright (c) 2018 ERGOBIT Consulting - www.ergobit.org
# See LICENSE file for full copyright and licensing details.
# contact: info@ergobit.org

{
    'name': 'OHADA - Accounting',
    'summary': 'Chart of accounts & chart of taxes',
    'category': 'Accounting',
    'author' : 'ERGOBIT',
    'description': """
Accounting Chart for OHADA
================================

This module implements the accounting chart for OHADA countries. It includes:
    - the new SYSCOHADA chart of accounts as of 2018,
    - fonctional enhancements of the CoA to prepare automatic financial statements which is done in module l10n_ohada_reports,
    - a basic chart of taxes,
    - a basic chart for social declarations,
    - automatic determination accounts and taxes in invoicing.

Countries that belong to OHADA are the following:
--------------------------------------------------
    Benin, Burkina Faso, Cameroon, Central African Republic, Comoros, Congo,
    Ivory Coast, Gabon, Guinea, Guinea Bissau, Equatorial Guinea, Mali, Niger,
    Replica of Democratic Congo, Senegal, Chad, Togo.
    
    """,
    'category': 'Accounting',
    'depends' : [
        'account', 
        'base_vat', 
    ],
    # 'data': [
    #     'data/res.country.group.csv',
    #     'data/menuitem.xml',
    #     'data/account_chart_template_data.xml',
    #     'data/account_tax_data.xml',
    #     'data/account_tax_template_data.xml',
    #     'data/account_brs_template_data.xml',
    #     'data/fiscal_position_template_data.xml',
    #     'data/account_chart_load_template.xml',
    #
    #     'views/account_view.xml',
    #     'views/res_config_settings_views.xml',
    # ],
    'auto_install': False,
    'installable': True,
    'license': 'OPL-1',
}
