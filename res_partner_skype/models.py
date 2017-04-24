# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    skype = fields.Char('Skype', size=128, index=True)
