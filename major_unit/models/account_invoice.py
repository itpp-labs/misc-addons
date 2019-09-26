
from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_trade_in_payment = fields.Boolean('Trade-in Payment', default=False)
