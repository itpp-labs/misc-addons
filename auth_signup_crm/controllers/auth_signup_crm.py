# -*- coding: utf-8 -*-
from openerp.addons.auth_signup_confirmation.controllers.auth_signup_confirmation import AuthConfirm
from openerp import http
from openerp.http import request

class AuthLead(AuthConfirm):
    def _send_email(self, *args, **kw):
        res = super(AuthLead, self)._send_email(*args, **kw)
        new_lead = request.env['crm.lead'].sudo().create(
             {
                'name': res['name'],
                'email_from': res['login'],
                'partner_id': res['partner_id'],
                'contact_name': res['name'],
                'user_id': res['user_id'],
             }
        )
        return res