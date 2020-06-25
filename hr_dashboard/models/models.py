# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, HRMS Leave Cancellation
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

from odoo import models, fields, api
from odoo.http import request
import datetime


class HrDashboard(models.Model):
    _name = 'hr.dashboard'
    _description = 'HR Dashboard'

    name = fields.Char("")

    @api.model
    def get_employee_info(self):
        """
        The function which is called from hr_dashboard.js.
        To fetch enough data from model hr and related dependencies.
        :payroll_dataset Total payroll generated according to months from model hr_payslip and hr_payslip_lines.
        :attendance_data Total worked hours and attendance details from models hr_attendace and hr_employee.
        :employee_table dict of datas from models hr_employee, hr_job, hr_department.
        :rtype dict
        :return: data
        """
        uid = request.session.uid
        cr = self.env.cr
        employee_id = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
        leave_search_view_id = self.env.ref('hr_holidays.view_hr_holidays_filter')
        timesheet_search_view_id = self.env.ref('hr_timesheet.hr_timesheet_line_search')
        job_search_view_id = self.env.ref('hr_recruitment.view_crm_case_jobs_filter')
        attendance_search_view_id = self.env.ref('hr_attendance.hr_attendance_view_filter')
        expense_search_view_id = self.env.ref('hr_expense.view_hr_expense_sheet_filter')
        leaves_to_approve = self.env['hr.leave'].sudo().search_count([('state', 'in', ['confirm', 'validate1'])])
        leaves_alloc_to_approve = self.env['hr.leave.allocation'].sudo().search_count([('state', 'in', ['confirm', 'validate1'])])
        timesheets = self.env['account.analytic.line'].sudo().search_count(
            [('project_id', '!=', False), ])
        timesheets_self = self.env['account.analytic.line'].sudo().search_count(
            [('project_id', '!=', False), ('user_id', '=', uid)])
        job_applications = self.env['hr.applicant'].sudo().search_count([])
        attendance_today = self.env['hr.attendance'].sudo().search_count([('check_in', '>=',
                            str(datetime.datetime.now().replace(hour=0, minute=0, second=0))),
                            ('check_in', '<=', str(datetime.datetime.now().replace(hour=23, minute=59, second=59)))])
        expenses_to_approve = self.env['hr.expense.sheet'].sudo().search_count([('state', 'in', ['submit'])])

        # payroll Datas for Bar chart
        query = """
            select to_char(to_timestamp (date_part('month', p.date_from)::text, 'MM'), 'Month') as Month, sum(pl.amount)
            as Total from hr_payslip p
            INNER JOIN hr_payslip_line pl
                on (p.id = pl.slip_id and pl.code = 'NET' and p.state = 'done')
            group by month, p.date_from order by p.date_from
        """
        cr.execute(query)
        payroll_data = cr.dictfetchall()
        payroll_label = []
        payroll_dataset = []
        for data in payroll_data:
            payroll_label.append(data['month'])
            payroll_dataset.append(data['total'])

        # Attendance Chart Pie
        query = """
            select sum(a.worked_hours) as worked_hours, e.name as employee
            from hr_attendance a
            inner join hr_employee e on(a.employee_id = e.id)
            group by e.name
        """
        cr.execute(query)
        attendance_data = cr.dictfetchall()
        attendance_labels = []
        attendance_dataset = []
        for data in attendance_data:
            attendance_labels.append(data['employee'])
            attendance_dataset.append(data['worked_hours'])

        query = """
            select e.name as employee, e.barcode as badge_id, j.name as job, d.name as department,
            e.work_phone, e.work_email, e.work_location, e.gender, e.birthday, e.marital, e.passport_id,
            e.medic_exam from hr_employee e inner join hr_job j on (j.id = job_id)
            inner join hr_department d on (e.department_id = d.id)

        """
        cr.execute(query)
        employee_table = cr.dictfetchall()
        if employee_id:
            categories = self.env['hr.employee.category'].sudo().search([('id', 'in', employee_id[0]['category_ids'])])
            data = {
                'categories': [c.name for c in categories],
                'leave_search_view_id': leave_search_view_id.id,
                'timesheet_search_view_id': timesheet_search_view_id.id,
                'job_search_view_id': job_search_view_id.id,
                'attendance_search_view_id': attendance_search_view_id.id,
                'expense_search_view_id': expense_search_view_id.id,
                'leaves_to_approve': leaves_to_approve,
                'leaves_alloc_to_approve': leaves_alloc_to_approve,
                'timesheets': timesheets,
                'timesheets_user': timesheets_self,
                'expenses_to_approve': expenses_to_approve,
                'job_applications': job_applications,
                'attendance_today': attendance_today,
                'payroll_label': payroll_label,
                'payroll_dataset': payroll_dataset,
                'attendance_labels': attendance_labels,
                'attendance_dataset': attendance_dataset,
                'emp_table': employee_table,
            }
            employee_id[0].update(data)
        return employee_id
