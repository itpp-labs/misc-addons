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

import logging
from openerp import api, models, fields
from datetime import datetime
from datetime import timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.http import root

_logger = logging.getLogger(__name__)

LOGOUT_TYPES = [('ur', 'User Request'),
                ('to', 'Timeout'),
                ('re', 'Rule enforcing')]


class IrSessions(models.Model):
    _name = 'ir.sessions'
    _description = "Sessions"

    user_id = fields.Many2one('res.users', 'User', ondelete='cascade', required=True)
    logged_in = fields.Boolean('Logged in', required=True, index=True)
    session_id = fields.Char('Session ID', size=100, required=True, index=True)
    date_login = fields.Datetime('Login', required=True)
    date_last_activity = fields.Datetime('Last Activity Date')
    expiration_seconds = fields.Integer('Seconds to Expire', index=True)
    expiration_date = fields.Datetime('Expiration date', compute='_compute_expiration_date', store=True, index=True)
    date_logout = fields.Datetime('Logout')
    logout_type = fields.Selection(LOGOUT_TYPES, 'Logout Type')
    session_lenght = fields.Datetime('Session Duration')
    # Add other fields about the sessions like Source IPs etc...

    _order = 'date_logout desc'

    # scheduler function to validate users session
    @api.model
    def validate_sessions(self):
        res = self.search([('logged_in', '=', True),
                           ('expiration_date', '!=', False),
                           ('expiration_date', '<=', fields.Datetime.now()),
                           ])
        res._close_session(logout_type='to')
        return True

    @api.model
    def update_last_activity(self, sid):
        res = self.sudo().search([('logged_in', '=', True), ('session_id', '=', sid)])
        res.write({'date_last_activity': fields.Datetime.now()})

    @api.one
    @api.depends('date_last_activity', 'expiration_seconds')
    def _compute_expiration_date(self):
        if not self.expiration_seconds:
            self.expiration_date = None
            return
        date_last_activity = datetime.strptime(self.date_last_activity, DEFAULT_SERVER_DATETIME_FORMAT)
        expiration_date = date_last_activity + timedelta(seconds=self.expiration_seconds)
        self.expiration_date = datetime.strftime(expiration_date, DEFAULT_SERVER_DATETIME_FORMAT)

    @api.multi
    def action_close_session(self):
        redirect = self._close_session()

        if redirect:
            url = '/web/login?db=%s' % self.env.cr.dbname
            return {
                'type': 'ir.actions.act_url',
                'target': 'self',
                'name': 'Session closed',
                'url': url
            }

    @api.multi
    def _close_session(self, logout_type=None):
        redirect = False
        for r in self:
            if r.user_id.id == self.env.user.id:
                redirect = True
            session = root.session_store.get(r.session_id)
            session.logout(keep_db=True, logout_type=logout_type, env=self.env)
            # we have to call delete function so user would not able
            # to continue use session
            root.session_store.delete(session)
            # we have to create new session with the same sid, so the
            # system will know which database user is trying to
            # use. In that case system shows Session Expired warning
            # instead of Not Found error.
            new_session = root.session_store.get(session.sid)
            new_session.db = session.db
            root.session_store.save(session)
        return redirect

    @api.multi
    def _on_session_logout(self, logout_type=None):
        self.write({'logged_in': False,
                    'date_logout': fields.datetime.now(),
                    'logout_type': logout_type,
                    })
