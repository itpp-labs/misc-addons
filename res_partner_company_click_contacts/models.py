# -*- coding: utf-8 -*-
from openerp import api
from openerp import fields
from openerp import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    record_url = fields.Char('Link to record', compute='compute_record_url')

    @api.one
    def compute_record_url(self):
        self.record_url = '#id=%s&model=%s' % (self.id, self._name)
