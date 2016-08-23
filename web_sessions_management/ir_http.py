# -*- coding: utf-8 -*-
import random
import openerp
from openerp import api
from openerp import models
from openerp.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def _auth_method_user(self):
        super(IrHttp, self)._auth_method_user()
        if random.random() < 0.01:
            with openerp.registry(request.cr.dbname).cursor() as cr:
                cr.autocommit(True)
                env = api.Environment(cr, request.uid, request.context)
                env['ir.sessions'].update_last_activity(request.session.sid)
                cr.commit()
