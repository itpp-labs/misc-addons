# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID

class account_analytic_account(osv.Model):
    _inherit = 'account.analytic.account'
    _columns = {
        'support_manager_id': fields.many2one('res.users', 'Support manager', select=True),
        'notetaker_id': fields.many2one('res.partner', 'Notetaker', select=True),
        'proof_reader_id': fields.many2one('res.partner', 'Proof reader', select=True),
        'consultant_id': fields.many2one('res.partner', 'Consultant', select=True),

        'commissioning_manager_id': fields.many2one('res.partner', 'Commissioning Manager', select=True),
        'business_manager_id': fields.many2one('res.partner', 'HR/Business Manager', select=True),

        'participant_ids': fields.many2many('res.partner', id1='contract_id', id2='partner_id', string='Case participants'),

        'state': fields.selection([
            ('template', 'Template'), # odoo
            ('draft','New'), # odoo

            ('pipeline_proactive', 'Pipeline - Proactive'), # new
            ('pipeline_reactive', 'Pipeline - Reactive'), # new
            ('open', 'Live'), # odoo renamed from 'In Progress'

            ('to_be_invoiced', 'To be Invoiced'), # new
            ('awaiting_payment', 'Awaiting Payment'), # new

            ('pending', 'Deferred'), # odoo renamed from 'To Renew'
            ('lost', 'Lost'), # new
            ('cancelled', 'Cancelled'), # odoo
            ('close','Completed'), # odoo renamed from 'Close'
        ], 'Status', required=True),
    }

class res_partner(osv.Model):
    _inherit = 'res.partner'

    _columns = {
        'participate_in_contract_ids': fields.many2many('account.analytic.account', id2='contract_id', id1='partner_id', string='Participate in contracts'),
    }

class crm_lead(osv.Model):
    _inherit = 'crm.lead'

class project_project(osv.Model):
    _inherit = 'project.project'

class project_task(osv.Model):
    _inherit = 'project.task'

