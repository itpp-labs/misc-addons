from odoo import api, models, fields, tools, _
from datetime import datetime, timedelta
from dateutil import parser
from dateutil import rrule
from dateutil.relativedelta import relativedelta


class CustomerCreatePickup(models.TransientModel):
    _name = "res.partner.create.pickups"
    _description = "create ride pickup"

    choose = fields.Selection([('demo_loaner', 'DropOff with demo loaner'), ('nodemo_loaner', 'DropOff with demo loaner'), (
        'pickup', 'Pickup at Home')], String='Choose', default='demo_loaner')
    process_type = fields.Selection(
        [('pickup', 'Pickup'), ('delivery', 'Delivery'), ], String='Choose', default='pickup')

    order_id = fields.Many2one(comodel_name='service.repair_order',
                               string='Vehicle Service Number',
                               readonly=False,
                               required=False)

    name = fields.Many2one(comodel_name='res.partner',
                           string='Customer Name',
                           readonly=False,
                           required=True)

    customer_vehicle = fields.Many2one(comodel_name='major_unit.major_unit',
                                       string='Vehicle',
                                       required=True,
                                       readonly=False,
                                       )

    mechanic_id = fields.Many2one(comodel_name='hr.employee',
                                  string='Mechanic',
                                  required=True,
                                  readonly=False,)

    @api.model
    def default_get(self, fields):
        mechanic = []
        res = super(CustomerCreatePickup, self).default_get(fields)
        if not res.get('partner_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'service.repair_order' and self.env.context.get('active_id'):
            res['name'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).partner_id.id
        if not res.get('order_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'service.repair_order' and self.env.context.get('active_id'):
            res['order_id'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).id
            res['customer_vehicle'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).major_unit_id.id
            res['process_type'] = self.env.context['process_type']
            res['mechanic_id'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).mechanic_id.id
        return res

    def create_new(self):
        context = dict(self._context or {})
        context.update({'technician_id':self.mechanic_id.id}),
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'drm.pickup',
            'context': context,
        }
