import random
from openerp import models
from openerp.http import request

class ir_http(models.AbstractModel):
    _inherit = 'ir.http'

    def _auth_method_user(self):
        super(ir_http, self)._auth_method_user()
        if random.random() < 0.01:
            request.env['ir.sessions'].update_last_activity(request.session.sid)
