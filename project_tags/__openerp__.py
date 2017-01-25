# -*- coding: utf-8 -*-
#
#
#    Sistemas ADHOC - ADHOC SA
#    https://launchpad.net/~sistemas-adhoc
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
#

{
    'name': 'Project Tags',
    'version': '1.0',
    'category': 'Projects & Services',
    'sequence': 14,
    'summary': '',
    'description': """
Project Tags
============

Tested on Odoo 8.0 d023c079ed86468436f25da613bf486a4a17d625
    """,
    'author': 'Sistemas ADHOC, IT-Projects LLC, Ivan Yelizariev',
    'website': 'www.sistemasadhoc.com.ar',
    'images': [
    ],
    'depends': [
        'project'
    ],
    'data': [
        'security/project_tags_group.xml',
        'view/project_view.xml',
        'view/project_tag_view.xml',
        'view/project_tags_menuitem.xml',
        'data/project_properties.xml',
        'data/project_tag_properties.xml',
        'data/project_track.xml',
        'data/project_tag_track.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
