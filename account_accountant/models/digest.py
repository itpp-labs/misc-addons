# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_account_bank_cash = fields.Boolean('Bank & Cash Moves')
    kpi_account_bank_cash_value = fields.Monetary(compute='_compute_kpi_account_total_bank_cash_value')

    def _compute_kpi_account_total_bank_cash_value(self):
        if not self.env.user.has_group('account.group_account_user'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            account_moves = self.env['account.move'].read_group([
                ('date', '>=', start),
                ('date', '<', end),
                ('journal_id.type', 'in', ['cash', 'bank']),
                ('company_id', '=', company.id)], ['journal_id', 'amount'], ['journal_id'])
            record.kpi_account_bank_cash_value = sum([account_move['amount'] for account_move in account_moves])

    def compute_kpis_actions(self, company, user):
        res = super(Digest, self).compute_kpis_actions(company, user)
        res.update({'kpi_account_bank_cash': 'account.open_account_journal_dashboard_kanban&menu_id=%s' % (self.env.ref('account.menu_finance').id)})
        return res
