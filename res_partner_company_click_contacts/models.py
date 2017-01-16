# -*- coding: utf-8 -*-
from openerp import api
from openerp import fields
from openerp import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    record_url = fields.Char('Link to record', compute='compute_record_url')

    @api.multi
    def compute_record_url(self):
        for r in self:
            r.compute_record_url_one()
        return True

    @api.multi
    def compute_record_url_one(self):
        self.ensure_one()
        self.record_url = '#id=%s&model=%s' % (self.id, self._name)
