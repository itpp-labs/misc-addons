#!/usr/bin/env python
##############################################################################
#
#    attachment_large_object module for OpenERP,
#    Copyright (C) 2014 Anybox (http://anybox.fr) Georges Racinet
#
#    This file is a part of attachment_large_object
#
#   anybox_perf is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    anybox_perf is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'attachment_large_object',
    'version': '0.1',
    'category': '',
    'description': """Provides a storage option for attachments as PostgreSQL large objects.

    To enable it after installation, go to Settings / Technical / System Parameters
    and add a configuration parameter with:

    - key: ir_attachment.location
    - value: postgresql:lobject

    """,
    'author': 'Anybox',
    'website': 'anybox.fr',
    'depends': ['base'],
    'init_xml': [],
    'update_xml': [],
    'test': [],
    'demo_xml': [],
    'js': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
