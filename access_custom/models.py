# -*- coding: utf-8 -*-
from openerp.osv import fields as old_fields
from openerp.osv import osv
from openerp import api, models, fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.exceptions import AccessError

class hr_employee(models.Model):
    '''
    Employee
    '''

    _inherit = 'hr.employee'

    def _payslip_count(self, cr, uid, ids, field_name, arg, context=None):
        try:
            res = super(hr_employee, self)._payslip_count(cr, uid, ids, field_name, arg, context)
        except AccessError, e:
            res = {
                employee_id: 0
                for employee_id in ids
            }
        return res
    _columns = {
        'payslip_count': old_fields.function(_payslip_count, type='integer', string='Payslips'),
    }

    def _get_access_to_employee_information(self):
        access_by_group = self.env.ref('access_custom.group_employee_private_information').id in self.env.user.groups_id.ids
        for r in self:
            r.access_to_employee_information = access_by_group or (r.user_id.id == self.env.uid)

    access_to_employee_information = fields.Boolean('Access to employee information', compute=_get_access_to_employee_information, store=False)


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(res_partner, self).read(fields=fields, load=load)
        for res in result:
            if not res.get('access_to_private_information', True):
                for k in ['street', 'street2', 'zip', 'city', 'state_id', 'country_id']:
                    res[k] = False
        return result

    @api.multi
    def _get_access_to_private_information(self):
        access_by_group = self.env.ref('access_custom.group_employee_private_information').id in self.env.user.groups_id.ids
        for r in self:
            r.access_to_private_information = not r.is_employee or access_by_group or (self.env.user.id in r.user_ids.ids)

    access_to_private_information = fields.Boolean('Access to private information', compute=_get_access_to_private_information, store=False)

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    archived = fields.Boolean('Archived', help='Only users with special rights have access to archived records. Untick "Active" field to hide record', default=False)


class project_project(models.Model):
    _inherit = 'project.project'

    archived = fields.Boolean('Archived', help='Only users with special rights have access to archived records. Untick "Active" field to hide record', default=False)

class project_task(models.Model):
    _inherit = 'project.task'

    archived = fields.Boolean('Archived', help='Only users with special rights have access to archived records. Untick "Active" field to hide record', related='project_id.archived')

