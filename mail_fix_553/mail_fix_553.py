# -*- coding: utf-8 -*-
import re
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv

import logging
_logger = logging.getLogger(__name__)

class mail_mail(osv.osv):
    _inherit = "mail.mail"

    def send(self, cr, uid, ids, context=None, **kwargs):
        catchall_alias = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.catchall.alias_from", context=context)
        catchall_domain = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.catchall.domain", context=context)

        correct_email_from = '@%s>?\s*$'%catchall_domain
        default_email_from = '%s@%s' % (catchall_alias, catchall_domain)


        for mail in self.browse(cr, SUPERUSER_ID, ids, context=context):
            email_from = mail.email_from
            if not email_from or re.search(correct_email_from, email_from) is None:
                mail.email_from = default_email_from
        return super(mail_mail, self).send(cr, uid, ids, context=context, **kwargs)
