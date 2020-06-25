from odoo import api, models, fields, tools, _
from datetime import datetime, timedelta
from dateutil import parser
from dateutil import rrule
from dateutil.relativedelta import relativedelta


class CustomerCreateInspection(models.TransientModel):
    _name = "res.partner.create.inspection"
    _description = "create ride inspection"

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
                                       readonly=False)

    mechanic_id = fields.Many2many(comodel_name='hr.employee',
                                   string='Mechanic',
                                   required=False,
                                   readonly=False)

    @api.model
    def default_get(self, fields):
        mechanic = []
        res = super(CustomerCreateInspection, self).default_get(fields)
        if not res.get('partner_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'service.repair_order' and self.env.context.get('active_id'):
            res['name'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).partner_id.id
        if not res.get('order_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'service.repair_order' and self.env.context.get('active_id'):
            res['order_id'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).id
            res['customer_vehicle'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).major_unit_id.id
            for mechanics in self.env['service.repair_order'].search([('id', '=', self.env.context['active_id'])], limit=1).mechanic_id:
                mechanic.append(mechanics.id)
            res['mechanic_id'] = mechanic

        return res

    def create_new(self):

        context = dict(self._context or {})
        context['technician_id'] = self.mechanic_id.id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'service.inspection',
            'context': context,
        }
