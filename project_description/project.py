# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

        # restricted field. Allowed group members only.
    description = fields.Text('description', groups="project_description.group_access_to_project_description")



class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        if isinstance(ids, int):
            ids = [ids]
        for id in ids:
            elmt = self.browse(cr, uid, id, context=context)
            res.append((id, elmt.name))
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
