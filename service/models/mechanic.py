#    Techspawn Solutions Pvt. Ltd.
#    Copyright (C) 2016-TODAY Techspawn(<http://www.Techspawn.com>).
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

import logging
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class Employee(models.Model):

    _inherit = "hr.employee"

    lift_id = fields.Many2one(comodel_name='drm.lift',
                              string='LIFT',
                              readonly=False,
                              required=False)
    workorder_id = fields.One2many('drm.workorders',
                                   'mechanic_id',
                                   string='Work-Order Id',
                                   readonly=False,
                                   )
    total_time=fields.Float('Total Work Duration(hrs/day)', store=True)
    hourly_rate=fields.Float('Hourly Rate (NZD)', store=True)
    efficiency=fields.Float('Efficiency', store=True)
    # start_date = fields.Datetime(related='workorder_id.start_date')
    # end_date = fields.Datetime(related='workorder_id.end_date')
    priority = fields.Selection([
        ('0', 'Low'), ('1', 'Medium'),
        ('2', 'High'), ('3', 'Highest')],
        'Employee Level', required=True, default='1')
    # employee_level = fields.Many2one('hr.level', string="Employee Level")

    @api.model
    def default_get(self, fields):
        res = super(Employee, self).default_get(fields)
        if self.env.context.get('default_department_id'):
            res['department_id'] = self.env['hr.department'].search(
                [('name', 'ilike', self.env.context.get('default_department_id'))])[0].id
        return res
