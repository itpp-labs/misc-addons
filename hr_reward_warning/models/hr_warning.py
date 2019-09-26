# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Jesni Banu (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrAnnouncementTable(models.Model):
    _name = 'hr.announcement'
    _description = 'HR Announcement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Code No:')
    announcement_reason = fields.Text(string='Title', states={'draft': [('readonly', False)]}, required=True, readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'Waiting For Approval'),
                              ('approved', 'Approved'), ('rejected', 'Refused')],
                             string='Status',  default='draft',
                             track_visibility='always')
    requested_date = fields.Date(string='Requested Date', default=datetime.now().strftime('%Y-%m-%d'))
    attachment_id = fields.Many2many('ir.attachment', 'doc_warning_rel', 'doc_id', 'attach_id4',
                                     string="Attachment", help='You can attach the copy of your Letter')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id, readonly=True,)
    is_announcement = fields.Boolean(string='Is general Announcement?')
    announcement_type = fields.Selection([('employee', 'By Employee'), ('department', 'By Department'), ('job_position', 'By Job Position')])
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_announcements', 'announcement', 'employee',
                                    string='Employees')
    department_ids = fields.Many2many('hr.department', 'hr_department_announcements', 'announcement', 'department',
                                      string='Departments')
    position_ids = fields.Many2many('hr.job', 'hr_job_position_announcements', 'announcement', 'job_position',
                                    string='Job Positions')
    announcement = fields.Html(string='Letter', states={'draft': [('readonly', False)]}, readonly=True)
    date_start = fields.Date(string='Start Date', default=fields.Date.today(), required=True)
    date_end = fields.Date(string='End Date', default=fields.Date.today(), required=True)

    @api.multi
    def reject(self):
        self.state = 'rejected'

    @api.multi
    def approve(self):
        self.state = 'approved'

    @api.multi
    def sent(self):
        self.state = 'to_approve'

    @api.constrains('date_start', 'date_end')
    def validation(self):
        if self.date_start > self.date_end:
            raise ValidationError("Start date must be less than End Date")

    @api.model
    def create(self, vals):
        if vals.get('is_announcement'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.announcement.general')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.announcement')
        return super(HrAnnouncementTable, self).create(vals)
