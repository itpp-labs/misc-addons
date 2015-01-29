from openerp import api, models, fields, SUPERUSER_ID

class mail_message(models.Model):
    _inherit = 'mail.message'

    @api.one
    @api.depends('author_id', 'notified_partner_ids')
    def _get_sent(self):
        self.sent = len(self.notified_partner_ids) > 1 or len(self.notified_partner_ids)==1 and self.notified_partner_ids[0].id != self.author_id.id

    sent = fields.Boolean('Sent', compute=_get_sent, help='Was message sent to someone', store=True)

class mail_notification(models.Model):
    _inherit = 'mail.notification'

    def _notify(self, cr, uid, message_id, **kwargs):
        super(mail_notification, self)._notify(cr, uid, message_id, **kwargs)
        self.pool['mail.message'].browse(cr, uid, message_id)._get_sent()
