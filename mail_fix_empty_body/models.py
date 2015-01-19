from openerp import api, models, fields, SUPERUSER_ID

class mail_compose_message(models.TransientModel):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        res = super(mail_compose_message, self).get_mail_values(cr, uid, wizard, res_ids, context)
        for id, d in res.iteritems():
            d['body'] = d.get('body') or ''
        return res
