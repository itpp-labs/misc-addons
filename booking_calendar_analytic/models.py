# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SaleOrderLineReminder(models.Model):
    _inherit = 'sale.order.line'

    contract_id = fields.Many2one('account.analytic.account', related='order_id.project_id', store=True)


class AccountAnalyticAccountBooking(models.Model):
    _inherit = 'account.analytic.account'

    def open_booking_order_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_ids = self.pool.get('sale.order').search(cr, uid, [('project_id', '=', context.get('search_default_project_id', False))])
        names = [record.name for record in self.browse(cr, uid, ids, context=context)]
        name = 'Booking Lines %s' % (','.join(names))
        view_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'booking_calendar.view_booking_order_line_tree')
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': view_id,
            'context': context,
            'domain': [('order_id', 'in', sale_ids)],
            'res_model': 'sale.order.line',
            'nodestroy': True,
        }
