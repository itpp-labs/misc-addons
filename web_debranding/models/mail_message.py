# -*- coding: utf-8 -*-
import logging
from odoo import models, api

from .ir_translation import debrand

_logger = logging.getLogger(__name__)

MODULE = '_web_debranding'


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def create(self, values):
        msg = super(MailMessage, self).create(values)
        if type(msg.subject) is str and 'application installed' in msg.subject:
            msg.body = debrand(self.env, msg.body, is_code=False)
        return msg
