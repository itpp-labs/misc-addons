# -*- coding: utf-8 -*-
from openerp.osv import fields as old_fields
from openerp.osv import osv
from openerp import api, models, fields, exceptions
from openerp.tools.translate import _
import time
import re

from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

def _get_proposal_id(self, cr, uid, ids, name, args, context=None):
    res = {}
    for r in self.browse(cr, uid, ids, context=context):
        proposal_id = self.pool['website_proposal.proposal'].search(cr, uid, [('res_id', '=', r.id), ('res_model', '=', self._name)], context=context)
        res[r.id] = proposal_id and proposal_id[0]
    return res

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    support_manager_id = fields.Many2one('res.users', 'Support manager', select=True)
    notetaker_id = fields.Many2one('res.partner', 'Notetaker', select=True)
    proof_reader_id = fields.Many2one('res.partner', 'Proof reader', select=True)
    consultant_id = fields.Many2one('res.partner', 'Consultant', select=True)

    commissioning_manager_id = fields.Many2one('res.partner', 'Commissioning Manager', select=True)
    business_manager_id = fields.Many2one('res.partner', 'HR/Business Manager', select=True)

    participant_ids = fields.Many2many('res.partner', id1='contract_id', id2='partner_id', string='Participants')

    lead_id = fields.Many2one('crm.lead', 'Lead \ Opportunity', required=False)
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

    _columns = {
        'proposal_id': old_fields.function(_get_proposal_id, type='many2one', obj='website_proposal.proposal', string='Proposal'),
    }

    _defaults = {
        'name': lambda self, cr, uid, context=None: context.get('project_name') or 'NONAME'
    }


class mail_compose_message(osv.Model):
    _inherit = 'mail.compose.message'

    def send_mail(self, cr, uid, ids, context=None):
        context = context or {}
        if context.get('default_model') == 'crm.lead' and context.get('mark_proposal_as_sent') and context.get('sale_case_id'):
            context = dict(context, mail_post_autofollow=True)
            self.pool.get('crm.lead').browse(cr, uid, context['sale_case_id'], context=context).signal_workflow('proposal_sent')
        return super(mail_compose_message, self).send_mail(cr, uid, ids, context=context)

class res_partner(models.Model):
    _inherit = 'res.partner'

    participate_in_contract_ids = fields.Many2many('account.analytic.account', id2='contract_id', id1='partner_id', string='Participate in contracts')

class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.depends('invoice_ids.deal_time')
    def _get_invoice_deal_time(self):
        self.invoice_deal_time = max([0] + [inv.deal_time or 0 for inv in self.invoice_ids])

    invoice_deal_time = fields.Integer(string='Invoice deal time', compute=_get_invoice_deal_time, store=True)

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

    sales_funnel_type = fields.Selection(related='stage_id.sales_funnel_type', readonly=True)
    sale_order_id = fields.Many2one('sale.order', 'Quotation \ Sale Order')
    sale_order_lines = fields.One2many('sale.order.line', 'order_id', string='Order lines', related='sale_order_id.order_line', readonly=False)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', related='sale_order_id.pricelist_id', readonly=False)
    date_order = fields.Datetime(string='Date order', related='sale_order_id.date_order', readonly=False)
    fiscal_position = fields.Many2one('account.fiscal.position', string='Fiscal Position', related='sale_order_id.fiscal_position', readonly=False)

    sale_order_state = fields.Selection('Sale order status', related='sale_order_id.state')
    color = fields.Integer('Color index', related='section_id.color')
    is_proposal_sent = fields.Boolean('Proposal sent', default=False)
    is_proposal_confirmed = fields.Boolean('Proposal confirmed', default=False)
    project_id = fields.Many2one('project.project', 'Project')
    contract_id = fields.Many2one('account.analytic.account', 'Contract', related='project_id.analytic_account_id')

    stage_closed_id = fields.Many2one('crm.case.stage', 'Last stage', help='Stage before close case')

    date_closed_custom = fields.Datetime(string='Date closed (custom)')

    @api.one
    @api.depends('date_closed_custom')
    def _get_deal_time(self):
        res = None
        start_date = self.create_date or old_fields.datetime.now()
        end_date = self.date_closed_custom or old_fields.datetime.now()
        d = datetime.strptime(end_date, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT)
        res = d.days + 1
        self.deal_time = res
    deal_time = fields.Integer(string='Deal time', compute=_get_deal_time, store=True)

    @api.model
    def update_deal_time(self):
        self.search([('date_closed_custom','=', False)])._get_deal_time()


    @api.one
    @api.depends('date_action', 'date_last_stage_update')
    def _get_last_action_time(self):
        res = None
        start_date = self.date_action or self.date_last_stage_update or old_fields.datetime.now()
        try:
            start_date = datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT)
        except:
            start_date = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        end_date = old_fields.datetime.now()
        end_date = datetime.strptime(end_date, DEFAULT_SERVER_DATETIME_FORMAT)

        d = end_date - start_date
        res = d.days
        self.last_action_time = res

    last_action_time = fields.Integer(string='Last Action', compute=_get_last_action_time, store=True)

    @api.one
    def action_create_sale_order(self):
        # TODO
        pass

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
    def action_set_state_sale_won(self, cr, uid, ids, context={}):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'

        r = self.browse(cr, uid, ids, context=context)[0]
        r.write({'is_proposal_confirmed': True})

        if r.project_id:
            r.set_sales_funnel('won')
            return True

        r.sale_order_id.action_button_confirm()

        sale_order_name = r.sale_order_id.name
        if not sale_order_name.endswith(' SO'):
            m = re.match('SE(\d*)(.*)', sale_order_name)

            if m:
                sale_order_name = '%s SO%s' % (m.group(1), m.group(2))
            else:
                sale_order_name = '%s SO' % sale_order_name
            r.sale_order_id.write({'name': sale_order_name})

        m = re.match('SE(\d*)(.*)', r.name)

        name = r.name
        if m:
            name = 'PE%s (SE)%s'% (m.group(1), m.group(2))
        vals = {
            'name':name,
            'partner_id': r.partner_id.id,
            'sale_case_id': r.id,
        }
        project_id = self.pool['project.project'].create(cr, uid, vals, context=context.copy())
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
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _('%s (copy)') % self.name
        new_id = super(crm_lead, self).copy(default)
        if self.proposal_id:
            proposal_default = {'res_id':new_id}
            new_proposal_id = self.proposal_id.copy(proposal_default)
        return new_id


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
                return {'warning': 'Quotation is not confirmed by customer'}

        return {}

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            new_stage = self.env['crm.case.stage'].browse(vals['stage_id'])
            for r in self:
                res = r.try_update_stage(new_stage)[0]
                if res.get('warning'):
                    raise exceptions.Warning(res.get('warning'))
                if new_stage.sales_funnel_type in ['won', 'lost']:
                    vals['stage_closed_id'] = r.stage_id.id
                    vals['date_closed_custom'] = fields.datetime.now()
        if 'user_id' in vals:
            for r in self:
                if r.sale_order_id and ( not r.sale_order_id.user_id or r.sale_order_id.user_id.id != vals['user_id']):
                    r.sale_order_id.user_id = vals['user_id']
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
    sale_case_ids = fields.One2many('crm.lead', 'project_id', string='Sale case')
    phonecall_count = fields.Integer('Phonecalls', compute='_get_phonecall_count')
    xtype = fields.Selection(selection=[
        ('external', 'External'),
        ('internal', 'Internal'),
    ], string="Project type", default='external')

    _columns = {
        # use own name, instead of account.analytic.account name
        'name': old_fields.char('Project Name', required=True),# TO DELETE
    }
    _defaults = {
        #'name': '_'
    }

    @api.multi
    def action_phonecall_count(self):
        lead_ids = (self.sale_case_ids.ids or []) + (self.sale_case_id and [self.sale_case_id.id] or [])

        res = self.pool.get('ir.actions.act_window').for_xml_id(self._cr, self.env.user.id, 'sale_mediation_custom', 'action_phonecall')

        res['domain'] = [('opportunity_id', 'in', lead_ids)]
        return res

    @api.one
    def _get_phonecall_count(self):
        lead_ids = (self.sale_case_ids.ids or []) + (self.sale_case_id and [self.sale_case_id.id] or [])
        self.phonecall_count = self.env['crm.phonecall'].search_count([('opportunity_id', 'in', lead_ids)])

    @api.v7
    def create(self, cr, uid, vals, context={}):
        if 'project_name' not in context:
            context['project_name'] = vals.get('name')
        return super(project_project, self).create(cr, uid, vals, context=context)

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

class website_proposal_template(osv.osv):
    _inherit = 'website_proposal.template'

    _defaults = {
        'res_model': 'crm.lead',
    }

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    date_invoice_end = fields.Date(string='Invoice End Date')

    @api.one
    @api.depends('date_invoice_end', 'date_invoice')
    def _get_deal_time(self):
        res = None
        start_date = self.date_invoice or fields.Date.today()
        end_date = self.date_invoice_end or fields.Date.today()
        d = datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        res = d.days + 1
        self.deal_time = res
    deal_time = fields.Integer(string='Deal time', compute=_get_deal_time, store=True)

    @api.multi
    def confirm_paid(self):
        self.write({'date_invoice_end': fields.Date.today()})
        return super(account_invoice, self).confirm_paid()
