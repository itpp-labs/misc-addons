# -*- coding: utf-8 -*-
from openerp import api
from openerp import models


class mail_message(models.Model):
    _inherit = 'mail.message'

    @api.cr_uid_context
    def message_read(self, cr, uid, ids=None, domain=None, message_unload_ids=None,
                     thread_level=0, context=None, parent_id=False, limit=None):
        if context and context.get('default_model') == 'res.partner':
            partner = self.pool['res.partner'].browse(cr, uid, context.get('default_res_id'))
            domain_by_id = domain and len(domain) == 1 and domain[0][0] == 'id' and domain[0][1] == '='
            if partner.is_company and not domain_by_id:
                ids = None
                domain = [('model', '=', 'res.partner'), ('res_id', 'in', [partner.id] + partner.child_ids.ids)]
        return super(mail_message, self).message_read(cr, uid, ids, domain, message_unload_ids, thread_level, context, parent_id, limit)
