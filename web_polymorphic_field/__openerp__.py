# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2014-2015 Augustin Cisterne-Kaas (ACK Consulting Limited)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{'name': 'Web Polymorphic Field',
 'version': '0.1',
 'category': 'Web',
 'depends': ['web'],
 'author': 'Augustin Cisterne-Kaas',
 'description': """
Add a new widget named "polymorphic"
The polymorphic field allow to dynamically store an id linked to any model in
Odoo instead of the usual fixed one in the view definition

E.g:

<field name="model" widget="polymorphic" polymorphic="object_id" />
<field name="object_id" />
""",
 # 'license': 'LGPL-3',
 'data': [
     'views/web_polymorphic_field.xml'
 ],
 'js': [
     'static/src/js/view_form.js'
 ],
 'installable': True,
 'application': False}
