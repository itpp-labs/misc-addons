# -*- coding: utf-8 -*-
from openerp.addons.auth_signup_confirmation.controllers.auth_signup_confirmation import AuthConfirm
from openerp import http
from openerp.http import request
import werkzeug

class AuthLead(AuthConfirm):
    @http.route('/web/signup/confirm', type='http', auth='public', website=True)
    def singnup_using_generated_link(self, *args, **kw):
        partner = request.env['res.partner'].sudo().search([('signup_token', '=', kw['token'])])
        user = request.env['res.users'].sudo().with_context(active_test=False).search([('partner_id', '=', partner.id)])
        if user.active:
            pass
        else:
            user.active = True
        new_lead = request.env['crm.lead'].sudo().create(
             {
                'name': partner.name,
                'partner_id': partner.id,
                'contact_name': partner.name,
                'user_id': user.id,
             }
        )
        return werkzeug.utils.redirect(kw.get('redirect') or '/web/login')
