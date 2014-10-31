# -*- coding: utf-8 -*-
from openerp.osv import fields as old_fields
from openerp.osv import osv
from openerp import api, models, fields
from openerp.tools.translate import _
import time
import re

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

def _get_proposal_id(self, cr, uid, ids, name, args, context=None):
    res = {}
    for r in self.browse(cr, uid, ids, context=context):
        proposal_id = self.pool['website_proposal.proposal'].search(cr, uid, [('res_id', '=', r.id), ('res_model', '=', self._name)], context=context)
        res[r.id] = proposal_id and proposal_id[0]
        return res

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    def _get_new_code(self, cr, uid, vals, context=None):
        today = old_fields.date.context_today(self, cr, uid, context=context)
        d = fields.Date.from_string(today)
        name = d.strftime('SE%y%m%d')
        ids = self.search(cr, uid, [('create_date', '>=', d.strftime(DEFAULT_SERVER_DATE_FORMAT))], context=context)
        if len(ids)>0:
            name = name + ('%02i'% (len(ids) + 1))
        return name

    support_manager_id = fields.Many2one('res.users', 'Support manager', select=True)
    notetaker_id = fields.Many2one('res.partner', 'Notetaker', select=True)
    proof_reader_id = fields.Many2one('res.partner', 'Proof reader', select=True)
    consultant_id = fields.Many2one('res.partner', 'Consultant', select=True)

    commissioning_manager_id = fields.Many2one('res.partner', 'Commissioning Manager', select=True)
    business_manager_id = fields.Many2one('res.partner', 'HR/Business Manager', select=True)

    participant_ids = fields.Many2many('res.partner', id1='contract_id', id2='partner_id', string='Participants')

    lead_id = fields.Many2one('crm.lead', 'Lead \ Opportunity', required=True, readonly=True)
    sale_order_id = fields.Many2one('sale.order', 'Quotation \ Sale Order', readonly=True)
    sale_order_lines = fields.One2many('sale.order.line', 'Order lines', related='sale_order_id.order_line')
    proposal_id = fields.Many2one('website_proposal.proposal', 'Proposal', related='sale_order_id.proposal_id', readonly=True)

    #create_date = fields.Date(default=fields.Date.context_today)
    color = fields.Integer('Color index')

    _columns = {
        'state': old_fields.selection(selection=[
            ('template', 'Template'), # odoo
            ('draft','New'), # odoo

            ('lead','Lead'),

            ('opp_identified', 'Prospect identified'),
            ('opp_qualified', 'Prospect qualified'),
            ('quot_proposal_preparation', 'Proposal preparation'),
            ('quot_proposal_sent', 'Proposal Sent'),

            ('quot_contract_preparation', 'Contract preparation'),
            ('quot_contract_sent', 'Contract sent'),

            ('sale_confirmation', 'Sale confirmation'),
            ('sale_won', 'Sale won'),

            ('to_be_invoiced', 'To be Invoiced'),
            ('awaiting_payment', 'Awaiting Payment'),

            ('lost', 'Lost'),
            ('cancelled', 'Cancelled'), # odoo
            ('close','Completed'), # odoo renamed from 'Close'
        ], string='Status', required=True),
    }
    _defaults = {
        'state': 'lead',
        'name': _get_new_code,
    }

    @api.one
    def action_set_state_opp_identified(self):
        self.state = 'opp_identified'

    @api.one
    def action_set_state_opp_qualified(self):
        self.state = 'opp_qualified'

    @api.one
    def action_set_state_quot_proposal_preparation(self):
        self.state = 'quot_proposal_preparation'

    @api.one
    def action_set_state_quot_proposal_sent(self):
        self.state = 'quot_proposal_sent'

    @api.v7
    def action_send_proposal(self, cr, uid, ids, context = None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        sale_case = self.browse(cr, uid, ids, context=context)[0]

        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'sale_mediation_custom', 'email_template_proposal')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict()
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': sale_case.sale_order_id.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            #'mark_so_as_sent': True,
            'sale_case_id': sale_case.id,
            'mark_proposal_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    @api.one
    def action_set_state_quot_contract_preparation(self):
        self.state = 'quot_contract_preparation'

    @api.one
    def action_set_state_quot_contract_sent(self):
        self.state = 'quot_contract_sent'

    @api.one
    def action_set_state_sale_confirmation(self):
        self.state = 'sale_confirmation'

    @api.v7
    def action_set_state_sale_won(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        r = self.browse(cr, uid, ids, context=context)[0]
        m = re.match('SE(\d*)(.*)', r.name)

        name = r.name
        print 'name', name, m
        if m:
            name = 'PE%s (SE)%s'% (m.group(1), m.group(2))
        print 'name', name
        vals = {
            'name': name,
            'type': 'contract',
            'analytic_account_id': r.id,
            'use_tasks': True,
        }
        project_id = self.project_create(cr, uid, r.id, vals, context=context)
        r.write({'use_tasks': True,
                 'state':'sale_won'})

        data_obj = self.pool.get('ir.model.data')
        form_view_id = data_obj._get_id(cr, uid, 'project', 'edit_project')
        form_view = data_obj.read(cr, uid, form_view_id, ['res_id'])
        print 'project_id', project_id

        return {
            'name': _('Project'),
            'view_type': 'form',
            'view_mode': 'kanban, tree, form',
            'res_model': 'project.project',
            'res_id': int(project_id),
            #'view_id': False,
            'views': [(form_view['res_id'],'form')],
            'type': 'ir.actions.act_window',
        }

    @api.v7
    def open_proposal(self, cr, uid, ids, context=None):
        r = self.browse(cr, uid, ids[0], context)
        return self.pool['website_proposal.proposal'].open_proposal(cr, uid, [r.proposal_id.id], context=context)


class mail_compose_message(osv.Model):
    _inherit = 'mail.compose.message'

    def send_mail(self, cr, uid, ids, context=None):
        context = context or {}
        if context.get('default_model') == 'sale.order' and context.get('mark_proposal_as_sent') and context.get('sale_case_id'):
            context = dict(context, mail_post_autofollow=True)
            self.pool.get('account.analytic.account').browse(cr, uid, context['sale_case_id'], context=context).action_set_state_quot_proposal_sent()
        return super(mail_compose_message, self).send_mail(cr, uid, ids, context=context)

class res_partner(models.Model):
    _inherit = 'res.partner'

    participate_in_contract_ids = fields.Many2many('account.analytic.account', id2='contract_id', id1='partner_id', string='Participate in contracts'),

class sale_order(osv.Model):
    _inherit = 'sale.order'
    _columns = {
        #'proposal_id': fields.many2one('website_proposal.proposal', 'Proposal'),
        'proposal_id': old_fields.function(_get_proposal_id, type='many2one', obj='website_proposal.proposal', string='Proposal'),

    }

#class sale_order(models.Model):
#    _inherit = 'sale.order'
#    def action_button_confirm(self, cr, uid, ids, context=None):
#        for order in self.browse(cr, uid, ids, context):
#            if not order.project_id:
#                raise osv.except_osv(
#                    _('Cannot confirm sale order!'),
#                    _('You have to define Contract/Analytic value before confirm sale order'))
#        return super(sale_order, self).action_button_confirm(cr, uid, ids, context)

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def action_create_sale_case(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        vals = {'lead_id': self.id,
                'partner_id': self.partner_id.id,
                'type': 'contract',
                'state':'lead'}
        sale_case_id = self.env['account.analytic.account'].create(vals)
        self.type = 'opportunity'

        form = self.env.ref('account_analytic_analysis.account_analytic_account_form_form', False)

        return {
            'name': _('Sale Case'),
            'view_type': 'form',
            'view_mode': 'tree, form, kanban',
            'res_model': 'account.analytic.account',
            'res_id': int(sale_case_id),
            #'view_id': False,
            'views': [(form.id, 'form')],
            'type': 'ir.actions.act_window',
        }

class project_project(models.Model):
    _inherit = 'project.project'
    _columns = {
        # use own name, instead of account.analytic.account name
        'name': old_fields.char('Project Name', required=True),
    }
    _defaults = {
        'name': '_'
    }

class project_task(models.Model):
    _inherit = 'project.task'

