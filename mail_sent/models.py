from openerp import api, models, fields, SUPERUSER_ID

class mail_message(models.Model):
    _inherit = 'mail.message'

    @api.one
    @api.depends('author_id', 'notification_ids')
    def _get_sent(self):
        self.sent = len(self.notified_partner_ids) > 1 or len(self.notified_partner_ids)==1 and self.notified_partner_ids[0].id != self.author_id.id

    sent = fields.Boolean('Sent', compute=_get_sent, help='Was message sent to someone', store=True)
