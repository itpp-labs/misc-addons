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
from openerp.osv import fields, osv, orm
from datetime import date, datetime, time, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.http import Response
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
            session_ids = self.browse(cr, SUPERUSER_ID, ids)
            for session in session_ids:
                session_ids = self.browse(cr, SUPERUSER_ID, ids)
                self.write(cr, uid, session.id,
                   {'logged_in': False,
                    'date_logout': fields.datetime.now(),
                    'logout_type': 'to'}, context=context)
        return True
    
    def action_close_session(self, cr, uid, ids, context):
        session_ids = self.browse(cr, SUPERUSER_ID, ids)
        for session_id in session_ids:
            response = werkzeug.BaseResponse()
            response.delete_cookie(session_id.session_id)
            #openerp.http.Root.session_store .SessionStore() .delete(session_id.session_id)
#             openerp.http.werkzeug.contrib.sessions.SessionStore(session_class=openerp.http.OpenERPSession).delete(session_id.session_id)
        return werkzeug.utils.redirect('/web/login?db=%s' % cr.dbname, 303)
                
                
