# -*- encoding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
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

from openerp.osv import fields
from openerp.osv import osv


class ResGroups(osv.osv):
    _inherit = 'res.groups'

    _columns = {
        'login_calendar_id': fields.many2one('resource.calendar',
                                             'Allow Login Calendar', company_dependent=True,
                                             help='The user will be only allowed to login in the calendar defined here.'),
        'no_multiple_sessions': fields.boolean('No Multiple Sessions', company_dependent=True,
                                               help='Select this to prevent user to start a session more than once'),
        'interval_number': fields.integer('Session Timeout', company_dependent=True, help='Timeout since last activity for auto logout'),
        'interval_type': fields.selection([('minutes', 'Minutes'),
                                           ('hours', 'Hours'), ('work_days', 'Work Days'),
                                           ('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')],
                                          'Interval Unit', company_dependent=True),
    }
