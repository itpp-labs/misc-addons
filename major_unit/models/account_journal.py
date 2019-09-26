
from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.journal'

    trade_in = fields.Boolean('Trade-in Journal', default=False)
