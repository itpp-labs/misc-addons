import hmac
from hashlib import sha256

from odoo import models, tools


class Users(models.Model):
    _inherit = "res.users"

    @tools.ormcache("sid")
    def _compute_session_token(self, sid):
        """ Compute a session token given a session id and a user id.

        DIFFERENCE from original: read database.secret via orm.
        See https://github.com/odoo/odoo/pull/22612#issuecomment-375040429

        TODO: we don't really need this redefinition, because in current version of the module column value is presented and up-to-date. Keep it until we are sure, that without this redefinition everything works after migration from previous versions fo the module.
        """
        database_secret = (
            self.env["ir.config_parameter"].sudo().get_param("database.secret")
        )
        # retrieve the fields used to generate the session token
        session_fields = ", ".join(sorted(self._get_session_token_fields()))
        self.env.cr.execute(
            """SELECT %s, %%s
                                FROM res_users
                                WHERE id=%%s"""
            % (session_fields),
            (database_secret, self.id),
        )
        if self.env.cr.rowcount != 1:
            self._invalidate_session_cache()
            return False
        data_fields = self.env.cr.fetchone()
        # generate hmac key
        key = (u"{}".format(data_fields)).encode("utf-8")
        # hmac the session id
        data = sid.encode("utf-8")
        h = hmac.new(key, data, sha256)
        # keep in the cache the token
        return h.hexdigest()
