# -*- coding: utf-8 -*-
from openerp.osv import fields as old_fields
from openerp.osv import osv
from openerp import api, models, fields, exceptions
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

    def _get_new_code(self, cr, uid, context=None):
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

    lead_id = fields.Many2one('crm.lead', 'Lead \ Opportunity', required=False)
    lead_id2 = fields.Many2one('crm.lead', 'Lead \ Opportunity', related='lead_id', readonly=True)
    lead_id_type = fields.Selection(string='Lead or Opportunity', related='lead_id.type')
    lead_id_priority = fields.Selection(string='Priority', related='lead_id.priority')
    lead_id_probability = fields.Float(string='Opportunity probability', related='lead_id.probability')
    lead_id_planned_revenue = fields.Float(string='Expected revenue', related='lead_id.planned_revenue')

    sale_order_id = fields.Many2one('sale.order', 'Quotation \ Sale Order')
    section_id = fields.Many2one('crm.case.section', 'Sales team')
    sale_order_lines = fields.One2many('sale.order.line', 'Order lines', related='sale_order_id.order_line')
    sale_order_state = fields.Selection('Sale order status', related='sale_order_id.state')

    #create_date = fields.Date(default=fields.Date.context_today)
    color = fields.Integer('Color index', related='section_id.color')

    STATE_SELECTION = [
        ('lead','Lead'),
        ('new','New'),
        ('qualified', 'Qualified'),
        ('quotation', 'Quotation'),
        ('negotiation', 'Negotiation'),
        ('sale_won', 'Sale won'),

        ('to_be_invoiced', 'To be Invoiced'),
        ('awaiting_payment', 'Awaiting Payment'),

        ('lost', 'Lost'),
        ('cancelled', 'Cancelled'), # odoo
        ('close','Close'),
        ('template', 'Template'), # odoo
    ]
    _columns = {
        'state': old_fields.selection(selection=STATE_SELECTION, string='Status', required=True),
        'proposal_id': old_fields.function(_get_proposal_id, type='many2one', obj='website_proposal.proposal', string='Proposal'),
    }
    _defaults = {
        'state': 'lead',
        'name': lambda self, cr, uid, context=None: context.get('project_name') or self._get_new_code(cr, uid, context=context),
    }

    @api.v7
    def create(self, cr, uid, vals, context=None):
        is_project = vals.get('project_ids')
        if not vals.get('lead_id') and not is_project:
            name = vals.get('name') or self._get_new_code(cr, uid, context=context)
            lead_id = self.pool['crm.lead'].create(cr, uid, {
                'partner_id': vals.get('partner_id'),
                'name': '%s Lead' % name,
            })
            vals['lead_id'] = lead_id
            vals['name'] = name
        return super(account_analytic_account, self).create(cr, uid, vals, context=context)

    @api.v7
    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        """ Override read_group to always display all states. """
        if groupby and groupby[0] == "state":
            # Default result structure
            # states = self._get_state_list(cr, uid, context=context)

            STATE_TO_DELETE = ['template', 'to_be_invoiced', 'awaiting_payment', 'lost', 'cancelled', 'close']
            states = self.STATE_SELECTION

            read_group_all_states = [{
                '__context': {'group_by': groupby[1:]},
                '__domain': domain + [('state', '=', state_value)],
                'state': state_value,
                'state_count': 0,
            } for state_value, state_name in states]
            # Get standard results
            read_group_res = super(account_analytic_account, self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby)
            # Update standard results with default results
            result = []
            for state_value, state_name in states:
                res = filter(lambda x: x['state'] == state_value, read_group_res)
                if not res:
                    if state_value in STATE_TO_DELETE:
                        continue
                    res = filter(lambda x: x['state'] == state_value, read_group_all_states)
                res[0]['state'] = [state_value, state_name]
                result.append(res[0])
            return result
        else:
            return super(account_analytic_account, self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby)

    def lead_to_opportunity(self):
        self.lead_id_type = 'opportunity'

    @api.one
    def action_set_state_new(self):
        self.state = 'new'
        self.lead_to_opportunity()

    @api.one
    def action_set_state_qualified(self):
        self.state = 'qualified'
        self.lead_to_opportunity()

    @api.one
    def action_set_state_quotation(self):
        self.state = 'quotation'
        self.lead_to_opportunity()

    @api.one
    def action_set_state_negotiation(self):
        self.state = 'negotiation'

    @api.v7
    def action_send_proposal(self, cr, uid, ids, context = None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        sale_case = self.browse(cr, uid, ids, context=context)[0]
        assert sale_case.sale_order_id.order_line, 'You have to specify order lines'

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
            'default_model': 'account.analytic.account',
            'default_res_id': sale_case.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
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

    #@api.v7 # workflow handler doesn't work with this decorator
    def action_set_state_sale_won(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'

        r = self.browse(cr, uid, ids, context=context)[0]
        if r.project_id:
            r.write({'state':'sale_won'})
            return True

        r.sale_order_id.action_button_confirm()

        m = re.match('SE(\d*)(.*)', r.name)

        name = r.name
        if m:
            name = 'PE%s (SE)%s'% (m.group(1), m.group(2))
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
    def edit_proposal(self, cr, uid, ids, context=None):
        r = self.browse(cr, uid, ids[0], context)
        return self.pool['website_proposal.proposal'].edit_proposal(cr, uid, [r.proposal_id.id], context=context)

    @api.v7
    def open_proposal(self, cr, uid, ids, context=None):
        r = self.browse(cr, uid, ids[0], context)
        return self.pool['website_proposal.proposal'].open_proposal(cr, uid, [r.proposal_id.id], context=context)


class mail_compose_message(osv.Model):
    _inherit = 'mail.compose.message'

    def send_mail(self, cr, uid, ids, context=None):
        context = context or {}
        if context.get('default_model') == 'account.analytic.account' and context.get('mark_proposal_as_sent') and context.get('sale_case_id'):
            context = dict(context, mail_post_autofollow=True)
            self.pool.get('account.analytic.account').browse(cr, uid, context['sale_case_id'], context=context).signal_workflow('proposal_sent')
        if context.get('default_model') == 'crm.lead' and context.get('mark_proposal_as_sent') and context.get('sale_case_id'):
            context = dict(context, mail_post_autofollow=True)
            self.pool.get('crm.lead').browse(cr, uid, context['sale_case_id'], context=context).signal_workflow('proposal_sent')
        return super(mail_compose_message, self).send_mail(cr, uid, ids, context=context)

class res_partner(models.Model):
    _inherit = 'res.partner'

    participate_in_contract_ids = fields.Many2many('account.analytic.account', id2='contract_id', id1='partner_id', string='Participate in contracts'),

class sale_order(osv.Model):
    _inherit = 'sale.order'
    _columns = {
        #'proposal_id': fields.many2one('website_proposal.proposal', 'Proposal'),
        'proposal_id': old_fields.function(_get_proposal_id, type='many2one', obj='website_proposal.proposal', string='Proposal'), # to delete

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

    def _get_new_code(self, cr, uid, context=None):
        today = old_fields.date.context_today(self, cr, uid, context=context)
        d = fields.Date.from_string(today)
        name = d.strftime('SE%y%m%d')
        ids = self.search(cr, uid, [('create_date', '>=', d.strftime(DEFAULT_SERVER_DATE_FORMAT))], context=context)
        if len(ids)>0:
            name = name + ('%02i'% (len(ids) + 1))
        return name


    sales_funnel_type = fields.Selection(related='stage_id.sales_funnel_type')
    sale_order_id = fields.Many2one('sale.order', 'Quotation \ Sale Order')
    sale_order_lines = fields.One2many('sale.order.line', 'Order lines', related='sale_order_id.order_line')
    sale_order_state = fields.Selection('Sale order status', related='sale_order_id.state')
    color = fields.Integer('Color index', related='section_id.color')
    is_proposal_sent = fields.Boolean('Proposal sent', default=False)
    is_proposal_confirmed = fields.Boolean('Proposal confirmed', default=False)
    project_id = fields.Many2one('project.project', 'Project')


    @api.multi
    def action_create_sale_case(self): # OLD
        #assert len(self) == 1, 'This option should only be used for a single id at a time.'
        sale_case_id = None
        for r in self:
            if r.contract_ids or not r.partner_id or r.type!='lead':
                continue
            vals = {'lead_id': r.id,
                    'partner_id': r.partner_id.id,
                    'section_id': r.section_id and r.section_id.id or False,
                    'type': 'contract',
                    'state':'lead'}
            sale_case_id = self.env['account.analytic.account'].create(vals)
            sale_case_id.write({'name': '%s %s' % (sale_case_id.name, r.name)})
            #r.type = 'opportunity'

        if len(self)>1 or not sale_case_id:
            return True

        form = self.env.ref('account_analytic_analysis.account_analytic_account_form_form', False)

        return {
            'name': _('Sale Case'),
            'view_type': 'form',
            'view_mode': 'tree, form, kanban',
            'res_model': 'account.analytic.account',
            'res_id': sale_case_id and int(sale_case_id),
            #'view_id': False,
            'views': [(form.id, 'form')],
            'type': 'ir.actions.act_window',
        }

    @api.one
    def set_sales_funnel(self, sales_funnel_type):
        stage_ids = self.env['crm.case.stage'].search([('sales_funnel_type', '=', sales_funnel_type), ('section_ids', '=', self.section_id.id), '|', ('type', '=', self.type), ('type', '=', 'both')])
        stage_ids = sorted(stage_ids, key=lambda x: x.sequence)
        self.stage_id = stage_ids[0]

    @api.one
    def action_set_state_quotation(self):
        self.set_sales_funnel('quotation')

    @api.one
    def action_set_state_negotiation(self):
        self.is_proposal_sent = True
        self.set_sales_funnel('negotiation')

    @api.one
    def action_set_state_sales_lost(self):
        self.set_sales_funnel('lost')


    @api.v7
    def action_send_proposal(self, cr, uid, ids, context = None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        sale_case = self.browse(cr, uid, ids, context=context)[0]
        if not sale_case.sale_order_id.order_line:
            raise exceptions.Warning('You have to specify order lines')

        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'sale_mediation_custom', 'email_template_proposal_lead')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict()
        ctx.update({
            'default_model': 'crm.lead',
            'default_res_id': sale_case.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
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

    #@api.v7 # workflow handler doesn't work with this decorator
    def action_set_state_sale_won(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'

        r = self.browse(cr, uid, ids, context=context)[0]
        r.write({'is_proposal_confirmed': True})

        if r.project_id:
            r.set_sales_funnel('won')
            return True

        r.sale_order_id.action_button_confirm()

        m = re.match('SE(\d*)(.*)', r.name)

        name = r.name
        if m:
            name = 'PE%s (SE)%s'% (m.group(1), m.group(2))
        ctx = context.copy()
        ctx['project_name'] = name
        vals = {
            'name':name,
            'sale_case_id': r.id,
        }
        project_id = self.pool['project.project'].create(cr, uid, vals, context=ctx)
        r.write({'project_id':project_id})
        r.set_sales_funnel('won')

        data_obj = self.pool.get('ir.model.data')
        form_view_id = data_obj._get_id(cr, uid, 'project', 'edit_project')
        form_view = data_obj.read(cr, uid, form_view_id, ['res_id'])

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
    def edit_proposal(self, cr, uid, ids, context=None):
        r = self.browse(cr, uid, ids[0], context)
        return self.pool['website_proposal.proposal'].edit_proposal(cr, uid, [r.proposal_id.id], context=context)

    @api.v7
    def open_proposal(self, cr, uid, ids, context=None):
        r = self.browse(cr, uid, ids[0], context)
        return self.pool['website_proposal.proposal'].open_proposal(cr, uid, [r.proposal_id.id], context=context)


    @api.one
    def try_update_stage(self, stage):
        old = self.stage_id.sales_funnel_type
        new = stage.sales_funnel_type
        if not (old and new):
            return {'warning': '"Sales funnel" field has to be specified for sale stage!'}

        if old=='lost' and new!='lead':
            return {'warning': 'From dead stage you can move sale case only to lead stage'}
        if new=='quotation':
            if not self.partner_id:
                return {'warning': 'You have to specify Customer'}
            if not self.proposal_id:
                return {'warning': 'You have to create proposal'}
        if new=='negotiation':
            #if old!='quotation':
            #    return {'warning': 'You can move to negotiation only after quotation'}
            if not self.is_proposal_sent:
                return {'warning': 'You have to sent proposal to client'}
        if new=='won':
            #if old!='negotiation':
            #    return {'warning': 'You have to pass Negotiation stages before move sale case to Won'}
            if not self.is_proposal_confirmed:
                return {'warning': 'Proposal is not confirmed by customer'}

        return {}

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            new_stage_id = self.env['crm.case.stage'].browse(vals['stage_id'])
            for r in self:
                res = r.try_update_stage(new_stage_id)[0]
                if res.get('warning'):
                    raise exceptions.Warning(res.get('warning'))
        result = super(crm_lead, self).write(vals)
        return result

    _columns = {
        'proposal_id': old_fields.function(_get_proposal_id, type='many2one', obj='website_proposal.proposal', string='Proposal'), # to delete
    }
    _defaults = {
        'name': _get_new_code,
    }

class project_project(models.Model):
    _inherit = 'project.project'
    sale_case_id = fields.Many2one('crm.lead', 'Sale case')
    _columns = {
        # use own name, instead of account.analytic.account name
        'name': old_fields.char('Project Name', required=True),# TO DELETE
    }
    _defaults = {
        #'name': '_'
    }

class project_task(models.Model):
    _inherit = 'project.task'


class crm_case_stage(models.Model):

    _inherit = 'crm.case.stage'

    sales_funnel_type = fields.Selection(selection=[
        ('lead', 'Lead'),
        ('quotation', 'Quotation'),
        ('negotiation', 'Negotiation'),
        ('won', 'Sales won'),
        ('lost', 'Lost'),
    ], string='Sales funnel', help='Type of stage. When you move sale case between stages of different types there will be some extra checks and actions.')
