# -*- coding: utf-8 -*-
# Copyright (c) 2019 ERGOBIT Consulting - www.ergobit.org
# See LICENSE file for full copyright and licensing details.
# contact: info@ergobit.org

{
    'name' : 'OHADA - Accounting Reports',
    'summary': 'View and create financial statements',
    'category': 'Accounting',
    'author' : 'ERGOBIT',
    'description': """
Accounting reports for OHADA
=============================

This module implements the financial statements of OHADA accounting system as of 2018:
    - the accounting reports,
    - the annexed notes,
    - the electronic visa by a chartered accountants and
    - further internal management reports.

Countries that use SYSCOHADA are the following:
------------------------------------------------
    Benin, Burkina Faso, Cameroon, Central African Republic, Comoros, Congo,
    Ivory Coast, Gabon, Guinea, Guinea Bissau, Equatorial Guinea, Mali, Niger,
    Democratic Republic of Congo, Senegal, Chad, Togo.

    """,

    'depends': ['l10n_ohada', 'account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'views/menuitem.xml',
        'views/ohada_dashboard_view.xml',
        'data/ohada_financial_report_main.xml',
        'data/ohada_financial_report_note.xml',
        'data/ohada_dashboard_data.xml',
        'views/ohada_report_view.xml',
        'views/report_financial.xml',
        'views/search_template_view.xml',
    ],
    'qweb': [
        'static/src/xml/account_report_template.xml',
        'static/src/xml/ohada_dashboard_template.xml',
    ],
    'auto_install': False,
    'installable': True,
    'license': 'OPL-1',
}
