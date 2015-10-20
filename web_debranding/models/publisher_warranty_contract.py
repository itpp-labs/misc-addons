from openerp import api, models, fields, SUPERUSER_ID


class publisher_warranty_contract(models.Model):
    _inherit = 'publisher_warranty.contract'

    def update_notification(self, cr, uid, ids, cron_mode=True, context=None):
        pass
