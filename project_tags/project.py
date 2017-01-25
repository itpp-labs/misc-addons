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


class Project(osv.osv):

    """"""

    _name = 'project.project'
    _inherits = {}
    _inherit = ['project.project']

    _columns = {
        'project_tag_ids': fields.many2many('project_tags.project_tag', 'project_tags___project_tag_ids_rel', 'project_id', 'project_tag_id', string='Tags'),
    }

    _defaults = {
    }

    _constraints = [
    ]


Project()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
