# -*- coding: utf-8 -*-

import re
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID

class mail_mail(osv.Model):
    _inherit = "mail.mail"
    def send(self, cr, uid, ids, context=None, **kwargs):
        catchall_alias = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.catchall.alias", context=context)
        catchall_domain = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.catchall.domain", context=context)

        fix_ids = []
        for mail in self.browse(cr, SUPERUSER_ID, ids, context=context):
            if re.search('@%s>?\s*$'%catchall_domain, mail.email_from) is None:
                print 'fix:', mail.email_from
                fix_ids.append(mail.id)

        email_from = '%s@%s' % (catchall_alias, catchall_domain)
        print 'new email', email_from

        if fix_ids:
            self.write(cr, uid, fix_ids, {'email_from': email_from}, context=context)

        return super(mail_mail, self).send(cr, uid, ids, context=context, **kwargs)
