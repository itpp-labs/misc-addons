import random
import openerp
from openerp import api, models, SUPERUSER_ID
from openerp.http import request


class ir_http(models.AbstractModel):
    _inherit = 'ir.http'

    def _auth_method_user(self):
        super(ir_http, self)._auth_method_user()
        if random.random() < 0.01:
            with openerp.registry(request.cr.dbname).cursor() as cr:
                cr.autocommit(True)
                env = api.Environment(cr, request.uid, request.context)
                env['ir.sessions'].update_last_activity(request.session.sid)
                cr.commit()
