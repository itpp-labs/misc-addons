# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.http import request


SYSCOHADA_LIST = ['BJ', 'BF', 'CM', 'CF', 'KM', 'CG', 'CI', 'GA', 'GN', 'GW', 'GQ', 'ML', 'NE', 'CD', 'SN', 'TD', 'TG']
DEPRECATED_ACCOUNTS = ['28180', '29180', '29190', '29390', '29490' '48160', '48170', '48180']

class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'
    '''
    At chart load, Odoo should not create a transfer account automatically, bcoz we want to use account 585% as transfer account. 
    For this, 
        1) set required=False for field transfer_account_code_prefix
        2) we first create CoA w/o the prefix (see line 32 in file account_chart_template_data.xml) to avoid the auto creation of transfer account
        3) but we assign the prefix later (see line 7240 in file account_chart_template_data.xml) 
            -> so late creation of transfer account can be done with prefix 585
    '''
    transfer_account_code_prefix = fields.Char(string='Prefix of the main transfer accounts', required=False)
    check_transfer_account_code_prefix = fields.Char(string='Prefix of the check transfer accounts', required=False)
    
    def _get_account_vals(self, company, account_template, code_acc, tax_template_ref):        
        vals = super(AccountChartTemplate, self)._get_account_vals(company, account_template, code_acc, tax_template_ref)
        if vals['code'][:5] in DEPRECATED_ACCOUNTS:
            vals['deprecated'] = True
        return vals
    
    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        journals = super(AccountChartTemplate, self)._prepare_all_journals(acc_template_ref, company, journals_dict)
        if self.env.user.company_id.country_id.code in SYSCOHADA_LIST:
            # For OHADA, sale/purchase journals must have a dedicated sequence for refunds
            for journal in journals:
                if journal['type'] == 'sale':
                    journal['code'] = 'FC'
                    journal['refund_sequence'] = True
                if journal['type'] == 'purchase':
                    journal['code'] = 'FF'
                    journal['refund_sequence'] = True
            # Add a journal for HR expenses
            journals.append({
                'type': 'purchase', 
                'name': 'Notes de frais',
                'code': 'NFR',
                'company_id': company.id,
                'default_credit_account_id': acc_template_ref.get(self.property_account_expense_categ_id.id),
                'default_debit_account_id': acc_template_ref.get(self.property_account_expense_categ_id.id),
                'show_on_dashboard': False,
                'color': 11,
                'sequence': 6
            })                    
        return journals
       
    def load_for_current_company(self, sale_tax_rate, purchase_tax_rate):
        self.ensure_one()
        res = super(AccountChartTemplate, self).load_for_current_company(sale_tax_rate, purchase_tax_rate)        
        # do not use `request.env` here, it can cause deadlocks
        if request and request.session.uid:
            current_user = self.env['res.users'].browse(request.uid)
            company = current_user.company_id
        else:
            # fallback to company of current user, most likely __system__
            # (won't work well for multi-company)
            company = self.env.user.company_id        
        # Set the transfer account on the company
        if self.check_transfer_account_code_prefix:
            company.check_transfer_account_id = self.env['account.account'].search([('code', '=like', self.check_transfer_account_code_prefix + '%')])[0]
        return res
