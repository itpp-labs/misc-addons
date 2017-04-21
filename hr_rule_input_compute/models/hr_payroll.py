# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval
import operator


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_inputs(self, contract_ids, date_from, date_to):
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        inputs_dict = dict()
        for payslip_input in res:
            inputs_dict[payslip_input['code']] = payslip_input
        globaldict = {
            'env': self.env,
            'operator': operator,
            'date_from': date_from,
            'date_to': date_to,
        }
        localdict = {
            'inputs': inputs_dict,
        }
        contracts = self.env['hr.contract'].browse(contract_ids)
        structure_ids = contracts.get_all_structures()
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).mapped('rule_ids')
        for rule in rule_ids:
            if rule.input_python_compute:
                safe_eval(rule.input_python_compute, globaldict, localdict, mode='exec', nocopy=True)
        return res


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    input_python_compute = fields.Text(string='Python Code')

    _sql_constraints = [
        ('hr_salary_rule_code_unique', 'UNIQUE (code)', 'Code must be unique.'),
    ]
