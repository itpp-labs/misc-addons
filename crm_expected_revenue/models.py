# -*- coding: utf-8 -*-
from openerp import api
from openerp import fields
from openerp import models


class CrmLead(models.Model):

    _inherit = 'crm.lead'

    @api.depends('planned_revenue', 'probability')
    @api.one
    def get_weighted_planned_revenue(self):
        self.weighted_planned_revenue = self.planned_revenue * self.probability / 100

    weighted_planned_revenue = fields.Float('Weighted expected revenue', compute=get_weighted_planned_revenue, store=True)
