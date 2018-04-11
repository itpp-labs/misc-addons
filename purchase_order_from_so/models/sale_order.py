from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def create_purchase_order(self):
        view = self.env.ref('purchase_order_from_so.purchase_order_wizard_form')
        vals = {
            'partner_id': self.partner_id.id,
            'date_order': self.date_order,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
        }
        print('oooooooooooooo', vals)
        wiz = self.env['purchase.order.wizard'].create(vals)
        wiz.create_po_lines_from_so(self)
        print('llllllllllllllllll', wiz, wiz.order_line_ids)
        return {
            'name': _('Create wizard'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': vals,
        }

    # return {
    #     'partner_id': s_order.partner_id.id,
    #     'date_order': s_order.date_order,
    #     'currency_id': s_order.currency_id.id,
    #     'company_id': s_order.company_id.id,
    #     # 'picking_type_id': self.company_id.street,
    #     'order_line': p_lines,
    # }
