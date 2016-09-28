# -*- coding: utf-8 -*-
import logging

from openerp import models
from openerp.release import version_info

_logger = logging.getLogger(__name__)


class PublisherWarrantyContract(models.AbstractModel):
    _inherit = 'publisher_warranty.contract'

    def update_notification(self, cr, uid, ids, cron_mode=True, context=None):
        is_enterprise = version_info[5] == 'e'
        _logger.debug('is_enterprise=%s', is_enterprise)
        if is_enterprise or self.pool.get('ir.config_parameter').get_param(cr, uid, 'web_debranding.send_publisher_warranty_url') == '1':
            return super(PublisherWarrantyContract, self).update_notification(cr, uid, ids, cron_mode, context)
        else:
            pass
