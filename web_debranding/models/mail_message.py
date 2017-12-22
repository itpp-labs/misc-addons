# -*- coding: utf-8 -*-
import logging
from odoo import models

from .ir_translation import debrand

_logger = logging.getLogger(__name__)

MODULE = '_web_debranding'


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def create(self, values):
        msg = super(MailMessage, self).create(values)
        if msg.subject and msg.subject.endswith('application installed!') and \
           msg.channel_ids.id and self.env.ref('mail.channel_all_employees').id and \
           self.env.ref('mail.channel_all_employees').id is 1:
            msg.body = debrand(self.env, msg.body, is_code=False)
        return msg
