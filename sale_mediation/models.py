# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID

class contract_category(osv.Model):
    _inherit = 'res.partner.category'
    _name = 'contract.category'

    _columns = {
        'parent_id': fields.many2one('contract.category', 'Parent Category', select=True, ondelete='cascade'),

        'partner_ids': fields.many2many('account.analytic.account', id1='category_id', id2='partner_id', string='Contracts'), # wrong name due to inherit
    }

class crm_lead(osv.Model):
    _inherit = 'crm.lead'

    _columns = {
        'contract_ids': fields.one2many('account.analytic.account', 'lead_id', 'Contracts')
    }

class project_project(osv.Model):
    _inherit = 'project.project'

    def _suppliers_subscribed(self, cr, uid, ids, name, args, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            supplier_ids = [r.id for r in p.supplier_ids]
            message_follower_ids = [r.id for r in p.message_follower_ids]
            res[p.id] = set(supplier_ids).issubset(set(message_follower_ids))
        return res

    def subscribe_suppliers(self, cr, uid, ids, context=None):
        for p in self.browse(cr, uid, ids, context=context):
            p.write({'message_follower_ids': [(4, r.id) for r in p.supplier_ids]})
        return True

    _columns = {
        'supplier_ids': fields.related('analytic_account_id', 'supplier_ids', string='Suppliers', type='many2many', relation='res.partner', readonly=True),
        'suppliers_subscribed': fields.function(_suppliers_subscribed, type='boolean', string='Are Suppliers Subscribed'),
    }

    def create(self, cr, uid, vals, context=None):
        partner_id = vals.get('partner_id') or context and context.get('partner_id')
        if partner_id:
            vals['message_follower_ids'] = vals.get('message_follower_ids') or []
            vals['message_follower_ids'].append((4, partner_id))
        return super(project_project, self).create(cr, uid, vals, context=context)


class project_task(osv.Model):
    _inherit = 'project.task'

    def _get_default_supplier(self, cr, uid, context=None):
        project_id = self._get_default_project_id(cr, uid, context)
        if project_id:
            project = self.pool.get('project.project').browse(cr, uid, project_id, context=context)
            supplier_ids = project and project.supplier_ids
            if supplier_ids:
                return supplier_ids[0].id
        return False

    _columns = {
        #'supplier_id': fields.many2one('res.partner', 'Supplier')
    }

    _defaults = {
        #'supplier_id': _get_default_supplier
    }


class account_analytic_account(osv.Model):
    _inherit = 'account.analytic.account'

    def _get_project_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        for a in self.browse(cr, uid, ids, context=context):
            res[a.id] = a.project_ids and a.project_ids[0] or None
        return res

    _columns = {
        'lead_id': fields.many2one('crm.lead', 'Lead \ Opportunity'),
        'project_ids': fields.one2many('project.project', 'analytic_account_id', 'Projects'),
        'project_id': fields.function(_get_project_id, type='many2one', obj='project.project', string='Project'),
        'category_id': fields.many2many('contract.category', id1='partner_id', id2='category_id', string='Tags'),
    }

    _defaults = {
        'fix_price_invoices': True,
        'supplier_fix_price_invoices': True,
    }
    def project_create(self, cr, uid, analytic_account_id, vals, context=None):
        '''
        This function is called at the time of analytic account creation and is used to create a project automatically linked to it if the conditions are meet.
        '''
        project_pool = self.pool.get('project.project')
        project_id = project_pool.search(cr, uid, [('analytic_account_id','=', analytic_account_id)])
        if not project_id and self._trigger_project_creation(cr, uid, vals, context=context):
            project_values = {
                'name': vals.get('name'),
                'analytic_account_id': analytic_account_id,
                'type': vals.get('type','contract'),
            }
            ctx = context.copy()
            ctx['partner_id'] = vals.get('partner_id')
            return project_pool.create(cr, uid, project_values, context=ctx)
        return False


class sale_order(osv.osv):
    _inherit = "sale.order"
    _defaults = {
        'project_id': lambda self, cr, uid, context: context.get('account_analytic_id', False)
    }

class crm_make_sale(osv.TransientModel):
    _inherit = "crm.make.sale"

    def makeOrder(self, cr, uid, ids, context=None):
        data = context and context.get('active_ids', []) or []
        context = context or {}
        account_analytic_id = None
        case_obj = self.pool.get('crm.lead')
        for make in self.browse(cr, uid, ids, context=context):
            for case in case_obj.browse(cr, uid, data, context=context):
                if case.account_analytic_id:
                    account_analytic_id = case.account_analytic_id
                    break
        context.update({'account_analytic_id': account_analytic_id})
        return super(crm_make_sale, self).makeOrder(cr, uid, ids, context)
