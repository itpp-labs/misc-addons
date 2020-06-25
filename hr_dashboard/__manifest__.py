# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, HRMS Dashboard
#    Copyright (C) 2019 Hilar AK All Rights Reserved
#    https://www.linkedin.com/in/hilar-ak/
#    <hilarak@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "HR Dashboard",

    'summary': """
        Dashboard For HR managers and Officers.
        """,

    'description': """
        Dashboard which includes employee details, total worked hours charts, payroll analysis,
        menus and count of approvals needed and logged in user details
    """,

    'author': "Hilar AK",
    'website': "https://www.linkedin.com/in/hilar-ak/",
    'category': "Generic Modules/Human Resources",
    'version': "12.0.1.0.0",
    'depends': [
        'base',
        'hr',
        'hr_expense',
        'hr_attendance',
        'hr_holidays',
        'hr_payroll',
        'hr_recruitment',
        'hr_timesheet',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_dashboard.xml',
    ],
    'qweb': [
        "static/src/xml/hr_dashboard.xml",
    ],
    'images': ["static/description/banner.gif"],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
