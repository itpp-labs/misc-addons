# -*- coding: utf-8 -*-
import logging
import werkzeug
from openerp import SUPERUSER_ID
from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
1
_logger = logging.getLogger(__name__)

class SignupDenied(Exception):
    pass

class UserExists(Exception):
    pass

class AuthConfirm(AuthSignupHome):
    def _signup_with_values(self, token, values):
        if token:
            return super(AuthConfirm, self)._signup_with_values(token, values)
        else:
            raise SignupDenied('Authentification Denied.')

    @http.route('/web/signup/thankyou/', type='http', auth='public')
    def thankyou(self, *args):
        # Show how to complete registration
        return http.request.render('auth_signup_confirmation.index')

    @http.route('/web/signup', type='http', auth='public')
    def web_auth_signup(self, *args, **kw):
        # super call without exception when user login with token. Its happends when user created via backend.
        try:
            return super(AuthConfirm, self).web_auth_signup(*args, **kw)
        except SignupDenied:
            pass
        try:
            res = self._send_email(*args, **kw)
            return werkzeug.utils.redirect('/web/signup/thankyou/')
        except UserExists:
            pass
        qcontext = self.get_auth_signup_qcontext()
        qcontext['error'] = 'A user with this email address is already registered'
        return request.render('auth_signup.signup', qcontext)

    @http.route('/web/signup/confirm', type='http', auth='public')
    def singnup_using_generated_link(self, *args, **kw):
        user = request.env['res.users'].sudo().with_context(active_test=False).search([
            ('partner_id.signup_token', '=', kw['token'])])
        if user.active:
            pass
        else:
            user.active = True
        return werkzeug.utils.redirect(kw.get('redirect') or '/web/login')

    def _send_email(self, *args, **kw):
        old_active_user = request.env['res.users'].sudo().search([('login', '=', kw['login'])])
        if old_active_user:
            raise UserExists("A user with this email address is already registered")
        old_not_active_user = request.env['res.users'].sudo().with_context(active_test=False).search([
            ('login', '=', kw['login'])])
        if old_not_active_user:
            new_user = old_not_active_user
            new_user.password = kw['password']
            new_partner = new_user.partner_id
            new_partner.email = kw['login']
        else:
            new_partner = request.env['res.partner'].sudo().with_context(signup_force_type_in_url='signup/confirm',
                                                                         signup_valid=True).create(
                {
                    'name': kw['name'],
                    'email': kw['login'],
                }
            )
            new_user = request.env["res.users"].sudo().with_context(no_reset_password=True).create({
                'name': kw['name'],
                'login': kw['login'],
                'alias_name': kw['name'],
                'active': False,
                'password': kw['password'],
                'partner_id': new_partner.id,
            })
        redirect_url = werkzeug.url_encode({'redirect': kw['redirect']})
        signup_url = new_partner.with_context(signup_force_type_in_url='signup/confirm',
            signup_valid=True)._get_signup_url(SUPERUSER_ID, [new_partner.id])[new_partner.id]
        if redirect_url != 'redirect=':
            signup_url += '&%s' % redirect_url
        # send email
        template = request.env.ref('auth_signup_confirmation.email_registration')
        email_ctx = {
            'default_model': 'res.partner',
            'default_res_id': new_partner.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'link': signup_url,
        }
        composer = request.env['mail.compose.message'].with_context(email_ctx).sudo().create({})
        composer.sudo().send_mail()
