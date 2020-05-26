
# -*- coding: utf-8 -*-

from odoo import models

class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _create_bank_journals(self, company, acc_template_ref):
        bank_journals = super(AccountChartTemplate, self)._create_bank_journals(company, acc_template_ref)
        if company.country_id.code in self.get_countries_posting_at_bank_rec():
            bank_journals.write({'post_at_bank_rec': True})
        return bank_journals
