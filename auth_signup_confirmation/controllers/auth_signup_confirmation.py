import werkzeug
from openerp import http
from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp.http import request


class SignupDenied(Exception):
    pass


class UserExists(Exception):
    pass


class AuthConfirm(AuthSignupHome):
    def _signup_with_values(self, token, values):
        if token:
            return super(AuthConfirm, self)._signup_with_values(token, values)
        else:
            raise SignupDenied("Authentification Denied.")

    @http.route("/web/signup/thankyou/", type="http", auth="public")
    def thankyou(self, *args):
        # Show how to complete registration
        return http.request.render("auth_signup_confirmation.index")

    @http.route("/web/signup", type="http", auth="public")
    def web_auth_signup(self, *args, **kw):
        # super call without exception when user login with token. Its happends when user created via backend.
        try:
            return super(AuthConfirm, self).web_auth_signup(*args, **kw)
        except SignupDenied:
            pass
        try:
            res = self._singup_with_confirmation(*args, **kw)
            # FIXME: don't trust to subject. Use more strong way to find message
            message = (
                request.env["mail.message"]
                .sudo()
                .search(
                    [
                        ("res_id", "=", res["partner_id"]),
                        ("subject", "=", "Confirm registration"),
                    ]
                )
            )
            message.sudo(res["user_id"]).set_message_done()
            registration_redirect_url = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("auth_signup_confirmation.url_singup_thankyou")
            )
            return werkzeug.utils.redirect(registration_redirect_url)
        except UserExists:
            pass
        qcontext = self.get_auth_signup_qcontext()
        qcontext["error"] = "A user with this email address is already registered"
        return request.render("auth_signup.signup", qcontext)

    @http.route("/web/signup/confirm", type="http", auth="public")
    def singnup_using_generated_link(self, *args, **kw):
        user = (
            request.env["res.users"]
            .sudo()
            .with_context(active_test=False)
            .search([("partner_id.signup_token", "=", kw["token"])])
        )
        if user.active:
            pass
        else:
            user.active = True
        return werkzeug.utils.redirect(kw.get("redirect") or "/web/login")

    def _singup_with_confirmation(self, *args, **kw):
        old_active_user = (
            request.env["res.users"].sudo().search([("login", "=", kw["login"])])
        )
        if old_active_user:
            raise UserExists("A user with this email address is already registered")
        old_not_active_user = (
            request.env["res.users"]
            .sudo()
            .with_context(active_test=False)
            .search([("login", "=", kw["login"])])
        )
        if old_not_active_user:
            new_user = old_not_active_user
            new_user.password = kw["password"]
            new_partner = new_user.partner_id
            new_partner.email = kw["login"]
        else:
            res_users = request.env["res.users"]
            values = {
                "login": kw["login"],
                "email": kw.get("email") or kw["login"],
                "password": kw["password"],
                "name": kw["name"],
                "alias_name": kw["name"],
            }
            new_user = (
                res_users.sudo()
                .with_context(
                    signup_force_type_in_url="signup/confirm", signup_valid=True
                )
                ._signup_create_user(values)
            )
            new_user.active = False
            new_partner = new_user.partner_id
        redirect_url = werkzeug.url_encode({"redirect": kw.get("redirect") or ""})
        new_partner.signup_prepare()
        signup_url = new_partner.with_context(
            signup_force_type_in_url="signup/confirm", signup_valid=True
        ).signup_url
        if redirect_url != "redirect=":
            signup_url += "&%s" % redirect_url
        # send email
        template = request.env.ref("auth_signup_confirmation.email_registration")
        new_partner.with_context(link=signup_url).message_post_with_template(
            template.id, composition_mode="comment"
        )
        return {"partner_id": new_partner.id, "user_id": new_user.id}
