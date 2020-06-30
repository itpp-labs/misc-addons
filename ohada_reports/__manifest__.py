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

    'depends': ['l10n_ohada', 'account_accountant', 'l10n_ohada_company'],
    'data': [
        'security/ir.model.access.csv',
        'views/menuitem.xml',
        'views/ohada_dashboard_view.xml',
        'views/ohada_sheets_layout.xml',
        'wizards/ohada_dash_options.xml',
        'wizards/ohada_dash_print_bundle.xml',
        'data/ohada_separate_formulas.xml',
        'data/ohada_report_info.xml',
        'data/ohada_report_note.xml',
        'data/ohada_report_main.xml',
        'data/ohada_report_sheet.xml',
        'data/ohada_report_cover.xml',
        'data/ohada_report_layout.xml',
        'data/ohada_dashboard.xml',
        'data/ohada_settings.xml',
        'views/report_config_view.xml',
        'views/report_template_view.xml',
        'views/search_template_view.xml',
        'views/ohada_dash_view.xml',
        'data/ohada_note_relevance.xml',
        'views/ohada_disclosure.xml',
        'data/ohada_dash.xml',
    ],
    'qweb': [
        'static/src/xml/change_options_button.xml',
        'static/src/xml/ohada_report_template.xml',
        'static/src/xml/ohada_dashboard_template.xml',
        'static/src/xml/note_relevance_view.xml',
    ],
    'external_dependencies': {'python': ['docusign_esign'], "bin": []},
    'auto_install': False,
    'installable': True,
    'license': 'OPL-1',
}
