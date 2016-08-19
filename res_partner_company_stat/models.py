# -*- coding: utf-8 -*-
from openerp.osv import fields, osv


class ResPartner(osv.osv):
    _inherit = 'res.partner'

    def _partners_for_stat(self, cr, uid, ids, context=None):
        all_ids = self.search(cr, uid, [('id', 'child_of', ids)], context=context)
        arr = []
        for partner in self.browse(cr, uid, all_ids, context):
            arr.append((partner.id, partner))
            if not partner.is_company and partner.parent_id:
                arr.append((partner.parent_id.id, partner))
        return arr

    # crm
    def _opportunity_meeting_phonecall_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, {'opportunity_count': 0, 'meeting_count': 0, 'phonecall_count': 0}), ids))
        arr = self._partners_for_stat(cr, uid, ids, context=context)

        # the user may not have access rights for opportunities or meetings
        try:
            for id, partner in arr:
                if id in ids:
                    res[id]['opportunity_count'] += len(partner.opportunity_ids)
                    res[id]['meeting_count'] += len(partner.meeting_ids)
        except:
            pass

        for id, partner in arr:
            if id in ids:
                res[id]['phonecall_count'] += len(partner.phonecall_ids)
        return res

    # sale
    def _sale_order_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, 0), ids))
        arr = self._partners_for_stat(cr, uid, ids, context=context)

        # The current user may not have access rights for sale orders
        try:
            for id, partner in arr:
                if id in ids:
                    res[id] += len(partner.sale_order_ids)
        except:
            pass
        return res

    # account
    def _journal_item_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, {'journal_item_count': 0, 'contracts_count': 0}), ids))
        arr = self._partners_for_stat(cr, uid, ids, context=context)

        MoveLine = self.pool('account.move.line')
        AnalyticAccount = self.pool('account.analytic.account')

        for id, partner in arr:
            partner_id = partner.id
            if id in ids:
                res[id]['journal_item_count'] += MoveLine.search_count(cr, uid, [('partner_id', '=', partner_id)], context=context)
                res[id]['contracts_count'] += AnalyticAccount.search_count(cr, uid, [('partner_id', '=', partner_id)], context=context)

        return res

    # project
    def _task_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, 0), ids))
        arr = self._partners_for_stat(cr, uid, ids, context=context)
        Task = self.pool['project.task']

        for id, partner in arr:
            partner_id = partner.id
            if id in ids:
                res[id] += Task.search_count(cr, uid, [('partner_id', '=', partner_id)], context=context)

        return res

    _columns = {
        'opportunity_count': fields.function(_opportunity_meeting_phonecall_count, string="Opportunity", type='integer', multi='opp_meet'),
        'meeting_count': fields.function(_opportunity_meeting_phonecall_count, string="# Meetings", type='integer', multi='opp_meet'),
        'phonecall_count': fields.function(_opportunity_meeting_phonecall_count, string="Phonecalls", type="integer", multi='opp_meet'),
        'sale_order_count': fields.function(_sale_order_count, string='# of Sales Order', type='integer'),
        'contracts_count': fields.function(_journal_item_count, string="Contracts", type='integer', multi="invoice_journal"),
        'journal_item_count': fields.function(_journal_item_count, string="Journal Items", type="integer", multi="invoice_journal"),
        'task_count': fields.function(_task_count, string='# Tasks', type='integer'),
    }
