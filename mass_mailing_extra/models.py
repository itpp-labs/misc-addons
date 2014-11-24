from openerp import api,models,fields

class MailMailStats(models.Model):

    _inherit = 'mail.mail.statistics'

    partner_ids = fields.Many2many('res.partner', related='mail_mail_id.recipient_ids', string='Partners')

    @api.one
    def _get_partner_ids_text(self):
        res = []
        for p in self.partner_ids:
            res.append('%s <%s>' % (p.name, p.email))
        self.partner_ids_text = ', '.join(res)

    partner_ids_text = fields.Char('Partners', compute=_get_partner_ids_text)
