from openerp import api, models, fields


class mail_message(models.Model):
    _inherit = 'mail.message'

    @api.one
    @api.depends('author_id', 'notified_partner_ids')
    def _get_sent(self):
        self_sudo = self.sudo()
        self_sudo.sent = len(self_sudo.notified_partner_ids) > 1 or len(self_sudo.notified_partner_ids) == 1 and self_sudo.author_id and self_sudo.notified_partner_ids[0].id != self_sudo.author_id.id

    sent = fields.Boolean('Sent', compute=_get_sent, help='Was message sent to someone', store=True)


class mail_notification(models.Model):
    _inherit = 'mail.notification'

    def _notify(self, cr, uid, message_id, **kwargs):
        super(mail_notification, self)._notify(cr, uid, message_id, **kwargs)
        self.pool['mail.message'].browse(cr, uid, message_id)._get_sent()


class mail_compose_message(models.TransientModel):

    _inherit = 'mail.compose.message'
    sent = fields.Boolean('Sent', help='dummy field to fix inherit error')

