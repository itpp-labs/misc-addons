# -*- coding: utf-8 -*-
# Copyright 2014-2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2015 s0x90 <https://github.com/s0x90>
# Copyright 2016 x620 <https://github.com/x620>
# Copyright 2016 manawi <https://github.com/manawi>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html).
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


from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    # restricted field. Allowed group members only.
    description = fields.Text('description', groups="project_description.group_access_to_project_description")


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def name_get(self):
        res = []
        if not self.ids:
            return res
        if isinstance(self.ids, (int, long)):
            self.ids = [self.ids]
        for id in self.ids:
            elmt = self.browse(id)
            res.append((id, elmt.name))
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
