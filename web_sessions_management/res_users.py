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
from datetime import datetime
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.addons.base.ir.ir_cron import _intervalTypes
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ResUsers(osv.osv):
    _inherit = 'res.users'

    _columns = {
        'login_calendar_id': fields.many2one('resource.calendar',
                                             'Allowed Login Calendar', company_dependent=True,
                                             help='The user will be only allowed to login in the calendar defined here.'),
        'no_multiple_sessions': fields.boolean('No Multiple Sessions', company_dependent=True,
                                               help='Select this to prevent user to start a session more than once'),
        'interval_number': fields.integer('Session Timeout', company_dependent=True, help='Timeout since last activity for auto logout'),
        'interval_type': fields.selection([('minutes', 'Minutes'),
                                           ('hours', 'Hours'), ('work_days', 'Work Days'),
                                           ('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')],
                                          'Interval Unit', company_dependent=True),
        'session_ids': fields.one2many('ir.sessions', 'user_id', 'User Sessions')
    }

    # get earlier expiring date
    def get_expiring_date(self, cr, uid, id, context):
        now = datetime.now()
        user_obj = request.registry.get('res.users')
        user_id = user_obj.browse(cr, SUPERUSER_ID, id, context=context)
        g_exp_date = now + _intervalTypes['weeks'](1)
        if id != SUPERUSER_ID:
            if user_id.interval_type:
                u_exp_date = now + _intervalTypes[user_id.interval_type](user_id.interval_number)
            else:
                u_exp_date = g_exp_date
            g_no_multiple_sessions = False
            # u_no_multiple_sessions = user_id.no_multiple_sessions
            for group in user_id.groups_id:
                if group.no_multiple_sessions:
                    g_no_multiple_sessions = True
                if group.interval_type:
                    t_exp_date = now + _intervalTypes[group.interval_type](group.interval_number)
                    if t_exp_date < g_exp_date:
                        g_exp_date = t_exp_date
            if g_no_multiple_sessions:
                # u_no_multiple_sessions = True
                pass
            if g_exp_date < u_exp_date:
                u_exp_date = g_exp_date
        else:
            u_exp_date = g_exp_date
        seconds = u_exp_date - now
        return datetime.strftime(u_exp_date, DEFAULT_SERVER_DATETIME_FORMAT), seconds.seconds
