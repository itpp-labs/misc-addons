
from odoo import models, api


class AccountAbstractPayment(models.AbstractModel):
    _inherit = 'account.abstract.payment'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        context = self.env.context
        res = super(AccountAbstractPayment, self)._onchange_journal()
        if context.get('active_model') == 'account.invoice' and context.get('active_id'):
            invoice = self.env['account.invoice'].browse(context['active_id'])
            self.amount = invoice.residual
            if self.journal_id.code == 'TRADE':
                sale_order = invoice.mapped('invoice_line_ids').mapped('sale_line_ids').mapped('order_id')
                if sale_order.details_model == 'sale.deal':
                    self.amount = sum(
                         sale_order.trade_in_mu_ids.mapped('trade_equity'))
        return res
