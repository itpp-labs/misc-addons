# -*- coding: utf-8 -*-
#
#
#    Project Tags
#    Copyright (C) 2013 Sistemas ADHOC
#    No email
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


from openerp.osv import osv, fields


class ProjectTag(osv.osv):

    """"""

    _name = 'project_tags.project_tag'
    _description = 'project_tag'

    _columns = {
        'name': fields.char(string='Name', required=True, size=64),
        'project_id': fields.many2many('project.project', 'project_tags___project_tag_ids_rel', 'project_tag_id', 'project_id', string='&lt;no label&gt;'),
    }

    _defaults = {
    }

    _constraints = [
    ]


ProjectTag()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
