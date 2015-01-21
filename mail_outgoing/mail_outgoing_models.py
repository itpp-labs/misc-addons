from openerp.osv import osv

class mail_message(osv.Model):
    _inherit = 'mail.message'

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        group_all_emails = self.pool.get('ir.model.data').xmlid_to_object(cr, uid, 'mail_outgoing.group_all_emails', context=context)

        user = self.pool['res.users'].browse(cr, uid, uid, context)
        user_groups = set(user.groups_id)
        if user_groups.issuperset(group_all_emails):
            return

        return super(mail_message, self).check_access_rule(cr, uid, ids, operation, context)

class mail_mail(osv.Model):
    _name = 'mail.mail'
    _inherit = ['mail.mail', 'ir.needaction_mixin']
    _needaction = True

    def _needaction_domain_get(self, cr, uid, context=None):
        return [('state','in', ['outgoing', 'exception'])]
