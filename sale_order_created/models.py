# -*- coding: utf-8 -*-
from openerp import models


class sale_order(models.Model):

    _inherit = 'sale.order'

    _track = {
        'state': {
            'sale_order_created.mt_order_created': lambda self, cr, uid, obj, ctx=None: obj.state in ['draft']

        }
    }
