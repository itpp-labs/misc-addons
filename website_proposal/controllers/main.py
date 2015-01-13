 # -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today OpenERP SA (<http://www.openerp.com>).
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

from openerp import SUPERUSER_ID, fields
from openerp.addons.web import http
from openerp.addons.web.http import request
import werkzeug
import datetime
import time

from openerp.tools.translate import _

class website_proposal(http.Controller):
    def request_info(self):
        wsgienv = request.httprequest.environ
        return '<em>IP: {REMOTE_ADDR}</em>'.format(**wsgienv)

    def post_request_info(self, proposal, message=None):
        body = ('%s<br/>%s') % (message or _('Request info'),
                             self.request_info())
        self.__message_post(body, proposal, type='comment', subtype=False)



    @http.route([
        "/website_proposal/<int:proposal_id>",
        "/website_proposal/<int:proposal_id>/<token>"
    ], type='http', auth="public", website=True)
    def view(self, proposal_id, token=None, message=False, **post):
        # use SUPERUSER_ID allow to access/view proposal for public user
        # only if he knows the private token
        uid = token and SUPERUSER_ID or request.uid
        proposal = request.registry.get('website_proposal.proposal').browse(request.cr, uid, proposal_id)
        now = time.strftime('%Y-%m-%d')
        if token:
            if token != proposal.access_token:
                return request.website.render('website.404')
            # Log only once a day
            if request.session.get('view_quote',False)!=now:
                request.session['view_quote'] = now
                body= ('%s<br/>%s') % (_('Proposal viewed by customer'),
                                       self.request_info())
                self.__message_post(body, proposal, type='comment')

        return self._render_proposal(uid, proposal, message)

    def _render_proposal(self, uid, proposal, message=None):
        record = request.registry.get(proposal.res_model).browse(request.cr, uid, proposal.res_id)
        values = {
            'proposal': proposal,
            'message': message and int(message) or False,
            'record': record,
            'order_valid': True,
            'company_id': proposal.company_id.id,
        }
        return request.website.render('website_proposal.proposal', values)

    @http.route(['/website_proposal/accept'], type='json', auth="public", website=True)
    def accept(self, proposal_id, token=None, signer=None, sign=None, **post):
        proposal_obj = request.registry.get('website_proposal.proposal')
        proposal = proposal_obj.browse(request.cr, SUPERUSER_ID, proposal_id)
        if token != proposal.access_token:
            return request.website.render('website.404')
        proposal.write({
            'state':'done',
            'sign':sign,
            'signer': signer,
            'sign_date': fields.Datetime.now()
        })
        #attachments=sign and [('signature.png', sign.decode('base64'))] or []
        attachments = []
        if sign:
            report_name = 'website_proposal.report_proposal'
            pdf = request.registry.get('report').get_pdf(request.cr, SUPERUSER_ID, [proposal_id], report_name)
            attachments = [('proposal-%s.pdf' % proposal_id, pdf)]

        #request.registry.get(proposal.res_model).signal_workflow(request.cr, SUPERUSER_ID, [proposal.res_id], 'proposal_confirmed', context=request.context)
        record = request.registry.get(proposal.res_model).browse(request.cr, SUPERUSER_ID, proposal.res_id, context=request.context)
        self.post_request_info(proposal, _('Confirmation request info'))
        record.signal_workflow('proposal_confirmed')
        message = _('Document signed by %s') % (signer,)
        self.__message_post(message, proposal, type='comment', subtype='mt_comment', attachments=attachments)
        return True

    @http.route(['/website_proposal/<int:proposal_id>/<token>/decline'], type='http', auth="public", website=True)
    def decline(self, proposal_id, token, **post):
        proposal_obj = request.registry.get('website_proposal.proposal')
        proposal = proposal_obj.browse(request.cr, SUPERUSER_ID, proposal_id)
        if token != proposal.access_token:
            return request.website.render('website.404')
        proposal.write({
            'state':'rejected',
        })
        #request.registry.get(proposal.res_model).action_cancel(request.cr, SUPERUSER_ID, [proposal_id])
        self.post_request_info(proposal, _('Declining request info'))
        record = request.registry.get(proposal.res_model).browse(request.cr, SUPERUSER_ID, proposal.res_id, context=request.context)
        record.signal_workflow('proposal_rejected')
        message = post.get('decline_message')
        if message:
            self.__message_post(message, proposal, type='comment', subtype='mt_comment')
        return werkzeug.utils.redirect("/website_proposal/%s/%s?message=2" % (proposal_id, token))

    @http.route(['/website_proposal/<int:proposal_id>/<token>/post'], type='http', auth="public", website=True)
    def post(self, proposal_id, token, **post):
        # use SUPERUSER_ID allow to access/view proposal for public user
        proposal_obj = request.registry.get('website_proposal.proposal')
        proposal = proposal_obj.browse(request.cr, SUPERUSER_ID, proposal_id)
        message = post.get('comment')
        if token != proposal.access_token:
            return request.website.render('website.404')
        if message:
            self.post_request_info(proposal, _('Comment info'))
            self.__message_post(message, proposal, type='comment', subtype='mt_comment')
        return werkzeug.utils.redirect("/website_proposal/%s/%s?message=1" % (proposal_id, token))

    def __message_post(self, message, proposal, type='comment', subtype=False, attachments=[]):
        request.session.body =  message
        cr, uid, context = request.cr, request.uid, request.context
        user = request.registry['res.users'].browse(cr, SUPERUSER_ID, uid, context=context)
        if 'body' in request.session and request.session.body:
            request.registry.get(proposal.res_model).message_post(cr, SUPERUSER_ID, proposal.res_id,
                    body=request.session.body,
                    type=type,
                    subtype=subtype,
                    author_id=user.partner_id.id,
                    context=context,
                    attachments=attachments
                )
            request.session.body = False
        return True


    @http.route(["/website_proposal/template/<model('website_proposal.template'):template>"], type='http', auth="user", website=True)
    def template_view(self, template, **post):
        values = { 'template': template }
        return request.website.render('website_proposal.template', values)
