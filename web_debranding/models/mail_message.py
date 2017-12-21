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
        if type(msg.subject) is unicode and \
           type(msg.channel_ids.description) is unicode and \
           type(msg.channel_ids.name) is unicode and \
           'application installed!' in msg.subject and \
           'General announcements for all employees.' == msg.channel_ids.description and \
           'general' == msg.channel_ids.name:
            msg.body = debrand(self.env, msg.body, is_code=False)
        return msg
