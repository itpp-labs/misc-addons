from openerp import api,models,fields,exceptions

from openerp.osv import fields as old_fields
from openerp.osv import osv
from openerp.tools.translate import _

def _get_active_id(self):
    return self._context.get('active_id')

def _get_active_ids(self):
    return self._context.get('active_ids')

from ..models import account_analytic_account as aaa

SIGNAL_SELECTION = [
    ('fake_lead_signal', 'lead'),
    ('new', 'new'),
    ('qualified', 'qualified'),
    ('proposal_created', 'proposal_created'),
    ('proposal_sent', 'proposal_sent'),
    ('proposal_confirmed', 'proposal_confirmed'),
]

def fix_sale_case_workflow(sale_case, new_signal):
    print 'fix_sale_case_workflow', sale_case, new_signal
    sale_case.delete_workflow()
    sale_case.create_workflow()
    for signal,label in SIGNAL_SELECTION:
        sale_case.signal_workflow(signal)
        if signal == new_signal:
            break

class sale_case_administration(models.TransientModel):
    _name = 'sale_mediation_custom.sale_case_administration'


    sale_case_id = fields.Many2one('account.analytic.account', default=_get_active_id)

    state = fields.Selection(related='sale_case_id.state')
    lead_id = fields.Many2one('crm.lead', related='sale_case_id.lead_id')
    sale_order_id = fields.Many2one('sale.order', related='sale_case_id.sale_order_id')
    signal = fields.Selection(selection=SIGNAL_SELECTION, string='Fix workflow')

    @api.one
    def action_apply(self):
        if self.signal:
            fix_sale_case_workflow(self.sale_case_id, self.signal)

class sale_case_administration_multi(models.TransientModel):
    _name = 'sale_mediation_custom.sale_case_administration_multi'


    sale_case_ids = fields.Many2many('account.analytic.account', default=_get_active_ids, relation='sale_mediation_custom_sale_case_admin_multi')

    state = fields.Selection(selection=aaa.STATE_SELECTION)

    signal = fields.Selection(selection=SIGNAL_SELECTION, string='Fix workflow')

    @api.one
    def action_apply(self):
        if self.state:
            self.sale_case_ids.state = self.state

        if self.signal:
            for r in self.sale_case_ids:
                fix_sale_case_workflow(r, self.signal)


class opportunity_to_sale_case(models.TransientModel):
    _name = 'sale_mediation_custom.opportunity_to_sale_case'

    opportunity_ids = fields.Many2many('crm.lead', default=_get_active_ids)
    state = fields.Selection(string='State for sales funnel', selection=aaa.STATE_SELECTION)

    @api.one
    def action_apply(self):
        for r in self.opportunity_ids:
            if r.contract_ids or not r.partner_id or r.type!='opportunity':
                continue
            vals = {'lead_id': r.id,
                    'partner_id': r.partner_id.id,
                    'section_id': r.section_id and r.section_id.id or False,
                    'type': 'contract',
                    'state':self.state}
            sale_case_id = self.env['account.analytic.account'].create(vals)
            sale_case_id.write({'name': '%s %s' % (sale_case_id.name, r.name)})

class create_proposal(models.TransientModel):
    _name = 'sale_mediation_custom.create_proposal'
    sale_case_id = fields.Many2one('account.analytic.account', default=_get_active_id)
    proposal_template_id = fields.Many2one('website_proposal.template')

    @api.v7
    def action_apply(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'

        ## CREATE OPPORTUNITY (from addons/sale_crm/wizard/crm_make_sale.py)
        context = dict(context or {})
        context.pop('default_state', False)

        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            #partner = make.partner_id
            partner = make.sale_case_id.lead_id.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                    ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            #for case in case_obj.browse(cr, uid, data, context=context):
            if True: # in order to save original indent
                assert make.proposal_template_id, 'You have to specify template'
                case = make.sale_case_id.lead_id
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                            ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Insufficient Data!'), _('No address(es) defined for this customer.'))

                vals = {
                    'name': '%s SO' % make.sale_case_id.name,
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                    'partner_id': partner.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': old_fields.date.context_today(self,cr,uid,context=context),
                    'fiscal_position': fpos,
                    'payment_term':payment_term,
                    'project_id': make.sale_case_id.id,
                }
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals, context=context)
                sale_order = sale_obj.browse(cr, uid, new_id, context=context)
                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)
                message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                case.message_post(body=message)

                ## CREATE proposal
                proposal_id = self.pool.get('website_proposal.template').create_proposal(cr, uid, make.proposal_template_id.id, make.sale_case_id.id, context=context)

                ## SAVE new status and sale_order
                make.sale_case_id.write({'sale_order_id':sale_order.id})
                make.sale_case_id.signal_workflow('proposal_created')

            #if make.close:
            #    case_obj.case_mark_won(cr, uid, data, context=context)
            #if not new_ids:
            #    return {'type': 'ir.actions.act_window_close'}
            #if len(new_ids)<=1:
            #    value = {
            #        'domain': str([('id', 'in', new_ids)]),
            #        'view_type': 'form',
            #        'view_mode': 'form',
            #        'res_model': 'sale.order',
            #        'view_id': False,
            #        'type': 'ir.actions.act_window',
            #        'name' : _('Quotation'),
            #        'res_id': new_ids and new_ids[0]
            #    }
            #else:
            #    value = {
            #        'domain': str([('id', 'in', new_ids)]),
            #        'view_type': 'form',
            #        'view_mode': 'tree,form',
            #        'res_model': 'sale.order',
            #        'view_id': False,
            #        'type': 'ir.actions.act_window',
            #        'name' : _('Quotation'),
            #        'res_id': new_ids
            #    }
            #return value


class create_proposal_lead(models.TransientModel):
    _name = 'sale_mediation_custom.create_proposal_lead'
    #sale_case_id = fields.Many2one('account.analytic.account', default=_get_active_id)
    sale_case_id = fields.Many2one('crm.lead', default=_get_active_id)
    proposal_template_id = fields.Many2one('website_proposal.template', string='Quotation template')

    @api.v7
    def action_apply(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'

        ## CREATE OPPORTUNITY (from addons/sale_crm/wizard/crm_make_sale.py)
        context = dict(context or {})
        context.pop('default_state', False)

        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            #partner = make.partner_id
            #partner = make.sale_case_id.lead_id.partner_id
            partner = make.sale_case_id.partner_id
            if not partner:
                raise exceptions.Warning('You have to specify Customer')
            partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                    ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            #for case in case_obj.browse(cr, uid, data, context=context):
            if True: # in order to save original indent
                assert make.proposal_template_id, 'You have to specify template'
                #case = make.sale_case_id.lead_id
                case = make.sale_case_id
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                            ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Insufficient Data!'), _('No address(es) defined for this customer.'))

                vals = {
                    'name': '%s SO' % make.sale_case_id.name,
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                    'partner_id': partner.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': old_fields.date.context_today(self,cr,uid,context=context),
                    'fiscal_position': fpos,
                    'payment_term':payment_term,
                    #'project_id': make.sale_case_id.id,
                }
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals, context=context)
                sale_order = sale_obj.browse(cr, uid, new_id, context=context)
                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)
                message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                case.message_post(body=message)

                ## CREATE proposal
                proposal_id = self.pool.get('website_proposal.template').create_proposal(cr, uid, make.proposal_template_id.id, make.sale_case_id.id, context=context)

                ## SAVE new status and sale_order
                make.sale_case_id.write({'sale_order_id':sale_order.id})
                make.sale_case_id.signal_workflow('proposal_created')

            #if make.close:
            #    case_obj.case_mark_won(cr, uid, data, context=context)
            #if not new_ids:
            #    return {'type': 'ir.actions.act_window_close'}
            #if len(new_ids)<=1:
            #    value = {
            #        'domain': str([('id', 'in', new_ids)]),
            #        'view_type': 'form',
            #        'view_mode': 'form',
            #        'res_model': 'sale.order',
            #        'view_id': False,
            #        'type': 'ir.actions.act_window',
            #        'name' : _('Quotation'),
            #        'res_id': new_ids and new_ids[0]
            #    }
            #else:
            #    value = {
            #        'domain': str([('id', 'in', new_ids)]),
            #        'view_type': 'form',
            #        'view_mode': 'tree,form',
            #        'res_model': 'sale.order',
            #        'view_id': False,
            #        'type': 'ir.actions.act_window',
            #        'name' : _('Quotation'),
            #        'res_id': new_ids
            #    }
            #return value

