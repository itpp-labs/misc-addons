from openerp import api, models, fields, SUPERUSER_ID


class publisher_warranty_contract(models.Model):
    _inherit = 'publisher_warranty.contract'

    def update_notification(self, cr, uid, ids, cron_mode=True, context=None):
        if int(self.env['ir.config_parameter'].get_param('web_debranding.send_publisher_warranty_url')):
            return super(publisher_warranty_contract, self).update_notification(cr, uid, ids, cron_mode, context)
        else:
            pass
