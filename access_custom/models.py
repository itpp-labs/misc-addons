# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.exceptions import AccessError

class hr_employee(osv.osv):
    '''
    Employee
    '''

    _inherit = 'hr.employee'

    def _payslip_count(self, cr, uid, ids, field_name, arg, context=None):
        print '_payslip_count'
        try:
            res = super(hr_employee, self)._payslip_count(cr, uid, ids, field_name, arg, context)
        except AccessError, e:
            res = {
                employee_id: 0
                for employee_id in ids
            }
        return res
    _columns = {
        'payslip_count': fields.function(_payslip_count, type='integer', string='Payslips'),
    }
