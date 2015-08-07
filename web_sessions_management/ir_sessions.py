# -*- encoding: utf-8 -*-
##############################################################################
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
##############################################################################

import logging
import openerp
from openerp import api
from openerp.osv import fields, osv, orm
from datetime import date, datetime, time, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.http import Response
from openerp.http import root
from openerp import http
from openerp.tools.translate import _
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug.wsgi import wrap_file

_logger = logging.getLogger(__name__)

LOGOUT_TYPES = [('ur', 'User Request'),
                ('to', 'Timeout'),
                ('re', 'Rule enforcing')]

class ir_sessions(osv.osv):
    _name = 'ir.sessions'
    _description = "Sessions"
    
    _columns = { 
        'user_id' : fields.many2one('res.users', 'User', ondelete='cascade',
            required=True),
        'logged_in': fields.boolean('Logged in', required=True, index=True),
        'session_id' : fields.char('Session ID', size=100, required=True),
        'date_login': fields.datetime('Login', required=True),
        'expiration_date' : fields.datetime('Expiration Date', required=True,
            index=True),
        'date_logout': fields.datetime('Logout'),
        'logout_type': fields.selection(LOGOUT_TYPES, 'Logout Type'),
        'session_lenght': fields.datetime('Session Duration'),
        # Add other fields about the sessions like Source IPs etc...
        }
    
    _order = 'date_logout desc'
    
    # scheduler function to validate users session
    def validate_sessions(self, cr, uid, context=None):
        ids = self.search(cr, SUPERUSER_ID,
            [('expiration_date', '<=', fields.datetime.now()),
             ('logged_in', '=', True)])
        if ids:
            self.browse(cr, SUPERUSER_ID, ids)._close_session(logout_type='to')
        return True

    @api.multi
    def action_close_session(self):
        redirect = self._close_session()

        if redirect:
            return werkzeug.utils.redirect('/web/login?db=%s' % cr.dbname, 303)

    @api.multi
    def _close_session(self, logout_type=None):
        redirect = False
        for r in self:
            if r.user_id.id == self.env.user.id:
                redirect = True
            session = root.session_store.get(r.session_id)
            session.logout(logout_type=logout_type, env=self.env)
            root.session_store.delete(session)
        return redirect

    @api.multi
    def _on_session_logout(self, logout_type=None):
        print '_on_session_logout', self
        self.write({'logged_in': False,
                    'date_logout': fields.datetime.now(),
                    'logout_type': logout_type,
                })
