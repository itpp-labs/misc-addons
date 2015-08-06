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
from openerp import SUPERUSER_ID
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug.wsgi import wrap_file
from openerp.http import request
from openerp.tools.translate import _
from openerp.http import Response
from openerp import http
from openerp.tools.func import lazy_property
#   
_logger = logging.getLogger(__name__)


class Root_tkobr(openerp.http.Root):
       
    def get_response(self, httprequest, result, explicit_session):
        if isinstance(result, Response) and result.is_qweb:
            try:
                result.flatten()
            except(Exception), e:
                if request.db:
                    result = request.registry['ir.http']._handle_exception(e)
                else:
                    raise
           
        if isinstance(result, basestring):
            response = Response(result, mimetype='text/html')
        else:
            response = result
           
        if httprequest.session.should_save:
            self.session_store.save(httprequest.session)
#          We must not set the cookie if the session id was specified using a http header or a GET parameter.
#          There are two reasons to this:
#          - When using one of those two means we consider that we are overriding the cookie, which means creating a new
#            session on top of an already existing session and we don't want to create a mess with the 'normal' session
#            (the one using the cookie). That is a special feature of the Session Javascript class.
#          - It could allow session fixation attacks.
        if not explicit_session and hasattr(response, 'set_cookie'):
            if not request.uid:
                request.uid = openerp.SUPERUSER_ID
            seconds = 90 * 24 * 60 * 60
            if httprequest.session.uid:
                user_obj = request.registry.get('res.users')
#                 expiring_date, seconds = user_obj.get_expiring_date(request.cr,
#                     request.uid, httprequest.session.uid, request.context)
            response.set_cookie('session_id', httprequest.session.sid, max_age=90*24*60*60) #seconds)
           
        return response
       
root = Root_tkobr()
openerp.http.Root.get_response = root.get_response

