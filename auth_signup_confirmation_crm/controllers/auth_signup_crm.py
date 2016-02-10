# -*- coding: utf-8 -*-
from openerp.addons.auth_signup_confirmation.controllers.auth_signup_confirmation import AuthConfirm
from openerp import http
from openerp.http import request
import werkzeug

class AuthLead(AuthConfirm):
    @http.route('/web/signup/confirm', type='http', auth='public')
    def singnup_using_generated_link(self, *args, **kw):
        user_state_before = request.env['res.users'].sudo().search([('partner_id.signup_token', '=', kw['token'])]).active
        res = super(AuthLead, self).singnup_using_generated_link(*args, **kw)
        user = request.env['res.users'].sudo().search([('partner_id.signup_token', '=', kw['token'])])
        if user.active and not user_state_before:
            new_lead = request.env['crm.lead'].sudo().create(
                 {
                    'name': user.partner_id.name,
                    'partner_id': user.partner_id.id,
                    'contact_name': user.partner_id.name,
                 }
            )
        return res
