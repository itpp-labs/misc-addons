# -*- coding: utf-8 -*-
from openerp import api
from openerp import fields
from openerp import models


class CrmLead(models.Model):

    _inherit = 'crm.lead'

    @api.depends('planned_revenue', 'probability')
    @api.multi
    def get_weighted_planned_revenue(self):
        for r in self:
            r.get_weighted_planned_revenue_one()
        return True

    @api.multi
    def get_weighted_planned_revenue_one(self):
        self.ensure_one()
        self.weighted_planned_revenue = self.planned_revenue * self.probability / 100

    weighted_planned_revenue = fields.Float('Weighted expected revenue', compute=get_weighted_planned_revenue, store=True)
