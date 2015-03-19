# -*- coding: utf-8 -*-
import re
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv

import logging
_logger = logging.getLogger(__name__)

class mail_mail(osv.osv):
    _inherit = "mail.mail"

    def _fix_email_from(cr, uid, email_from):
        catchall_alias = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.catchall.alias_from", context=context)
        catchall_domain = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.catchall.domain", context=context)

        correct_email_from = '@%s>?\s*$'%catchall_domain
        default_email_from = '%s@%s' % (catchall_alias, catchall_domain)

        if not email_from or re.search(correct_email_from, email_from) is None:
            email_from = default_email_from
        return email_from

    def create(self, cr, uid, values, context=None):
        if 'email_from' in values:
            values['email_from'] = self._fix_email_from(cr, uid, values['email_from'])

        return super(mail_mail, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if 'email_from' in values:
            values['email_from'] = self._fix_email_from(cr, uid, values['email_from'])

        return super(mail_mail, self).write(cr, uid, ids, values, context=context)
