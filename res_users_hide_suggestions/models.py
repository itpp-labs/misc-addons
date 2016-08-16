# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    display_suggestions_hidden = fields.Boolean('Suggestions were hidden', default=False, help="Tick to don't repeat removing suggestion ticks")
    _defaults = {
        'display_groups_suggestions': False,
        'display_employees_suggestions': False,
    }
