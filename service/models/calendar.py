from dateutil import relativedelta
import datetime
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import Warning


class PickupCenter(models.Model):
    _name = 'drm.pickup'
    _description = 'Work Center'

    state = fields.Selection([('confirm', 'Confirm'),
                              ('progress', 'Progress'),
                              ('done', 'Finished'),
                              ('cancel', 'Cancelled')],
                             string='Status',
                             default='confirm',
                             states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    resource_id = fields.Many2one('resource.resource',
                                  'Resource',
                                  ondelete='cascade',
                                  required=True,
                                  states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    note = fields.Text('Description',
                       help="Description of the Work Center.",
                       states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    is_service_event = fields.Boolean('Service Event',
                                      default=False,
                                      states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    choose = fields.Selection([('demo_loaner', 'DropOff with demo loaner'),
                               ('nodemo_loaner', 'DropOff with demo loaner'),
                               ('pickup', 'Pickup at Home')],
                              String='Choose',
                              default='demo_loaner',
                              states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    preferred_time = fields.Selection([('morning', 'Morning'),
                                       ('afternoon', 'Afternoon'),
                                       ('evening', 'Evening'),
                                       ('night', 'Night')
                                       ],
                                      String='Preferred Time',
                                      default='morning',
                                      states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    process_type = fields.Selection([('pickup', 'Pickup'),
                                     ('delivery', 'Delivery')],
                                    String='Type',
                                    required=True,
                                    default='pickup',
                                    states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    service_job = fields.Text(String='Service Job', states={
                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    distance = fields.Float(string="Distance", default="1", states={
                            'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    estimate = fields.Float(String='Estimate for repair visit', states={
                            'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    order_id = fields.Many2one(comodel_name='service.repair_order',
                               string='Repair Order',
                               readonly=False,
                               required=True,
                               domain="[('state', 'not in', ('INSPECT','LIFT','TEST','COMPLETE','DELIVER','CANCEL'))]",
                               states={'progress': [('readonly', True)], 'done': [('readonly', True)],  'cancel': [('readonly', True)]})
    name = fields.Char(string='Reference',
                       required=True,
                       copy=False,
                       readonly=True,
                       index=True,
                       default='New',
                       states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    partner_id = fields.Many2one(comodel_name='res.partner',
                                 string='Customer',
                                 domain="[('customer', '=', True)]",
                                 required=True,
                                 states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    vehicle_id = fields.Many2one(comodel_name='major_unit.major_unit',
                                 string='Vehicle',
                                 required=True,
                                 states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    date_planned_start = fields.Datetime(string='Deadline Start',
                                         copy=False,
                                         default=fields.Datetime.now,
                                         index=True, required=True,
                                         oldname="date_planned",
                                         states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    technician_id = fields.Many2one(comodel_name='hr.employee',
                                    string="Technician",      
                                    required=True,                          
                                    states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    street = fields.Char('Address 1', states={
                         'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    street2 = fields.Char('Address 2', states={
                          'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    zip = fields.Char('Zip code', change_default=True, states={
                      'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    city = fields.Char(
        'City', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    state_id = fields.Many2one("res.country.state",
                               string='State',
                               ondelete='restrict',
                               states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    country_id = fields.Many2one('res.country',
                                 string='Country',
                                 ondelete='restrict',
                                 states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    phone = fields.Char(
        'Phone', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    mobile = fields.Char(
        'Mobile', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.onchange('order_id')
    def on_change_repair_order(self):
        self.partner_id = self.order_id.partner_id.id
        self.vehicle_id = self.order_id.major_unit_id.id
        self.street = self.order_id.partner_id.street
        self.street2 = self.order_id.partner_id.street2
        self.country_id = self.order_id.partner_id.country_id.id
        self.state_id = self.order_id.partner_id.state_id.id
        self.city = self.order_id.partner_id.city
        self.zip = self.order_id.partner_id.zip
        self.phone = self.order_id.partner_id.phone
        self.mobile = self.order_id.partner_id.mobile

    @api.model
    def create(self, vals):
        previous_pickup = self.env['drm.pickup'].search(
            [('order_id', '=', vals['order_id'])])
        for pickup_order in previous_pickup:
            if pickup_order.process_type == vals['process_type'] and pickup_order.state != 'cancel':
                temp = "Pickup already requested for " + \
                    str(pickup_order.order_id.name)
                raise Warning(temp)
        vals['resource_id'] = self.env['hr.employee'].browse(
            vals['technician_id']).resource_id.id
        vals['name'] = vals['process_type'] + ' ' + \
            (self.env['ir.sequence'].next_by_code('drm.pickup') or 'New')

        repair_order = self.env['service.repair_order'].search(
            [('id', '=', vals['order_id'])], limit=1)
        if not 'partner_id' in vals.keys():
            vals['partner_id'] = repair_order.partner_id.id
        if not 'vehicle_id' in vals.keys():
            vals['vehicle_id'] = repair_order.major_unit_id.id
        if vals['process_type'] == 'pickup':
            repair_order.write({'pickup': True})
        if vals['process_type'] == 'delivery':
            repair_order.write({'delivery': True})
        result = super(PickupCenter, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        if 'process_type' in vals.keys():
            vals['name'] = vals['process_type'] + ' ' + \
                self.env['ir.sequence'].next_by_code('drm.pickup')
            mail_values = {
                'email_from': 'admin@noblerush.com',
                'email_to': self.partner_id.email,
                'subject': 'Reschedule Pickup And Delivery',
                'body_html': '<h2>Hi %s,</h2><h3>Your Service Ride Pickup has been successfully Rescheduled at %s</h3>' % (self.partner_id.name, self.date_planned_start),
                'notification': True,
            }
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()

        result = super(PickupCenter, self).write(vals)
        return result

    @api.multi
    @api.onchange('order_id')
    def pickup_vehicle(self):
        self.vehicle_id = self.order_id.major_unit_id
        self.partner_id = self.order_id.partner_id

    @api.multi
    @api.onchange('distance')
    def pickup_estimation(self):
        ir_values = self.env['ir.default']
        default_rate_after = ir_values.get(
            'pickup.price', 'rate_after') or 0.0
        default_rate = ir_values.get('pickup.price', 'rate') or 0.0
        default_fix_distance = ir_values.get(
            'pickup.price', 'fixed_distance') or 0.0

        if self.distance <= default_fix_distance:
            self.estimate = default_rate_after

        else:
            distance = self.distance - default_fix_distance
            self.estimate = (distance * default_rate) + default_rate_after

    @api.model
    def default_get(self, vals):
        """
        In this function default_service_event is checked
        and added by default in form view
        """
        mechanic = []
        res = super(PickupCenter, self).default_get(vals)
        if self.env.context.get('default_service_event'):
            res['is_service_event'] = self.env.context['default_service_event']

        if not res.get('order_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'service.repair_order' and self.env.context.get('active_id'):
            res['order_id'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).id
            res['vehicle_id'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).major_unit_id.id

        if not res.get('partner_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'service.repair_order' and self.env.context.get('active_id'):
            temp = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1)
            res['partner_id'] = temp.partner_id.id
            res['process_type'] = self.env.context['process_type']
            if 'technician_id' in self.env.context.keys():
                res['technician_id'] = self.env.context.get('technician_id')
        return res

    @api.multi
    def action_confirm(self, vals):
        mail_values = {
            'email_from': 'admin@noblerush.com',
            'email_to': self.partner_id.email,
            'subject': 'Booking Pickup And Delivery',
            'body_html': '<h2>Hi %s,</h2><h3>Your Service Ride Pickup has been Successfully Booked at %s</h3>' % (self.partner_id.name, self.date_planned_start),
            'notification': True,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
        self.write({'state': 'progress'})

    @api.multi
    def action_progress(self):
        if self.order_id.state in ['QUOTE', 'APPROVE', 'PARTS', 'INSPECT', 'LIFT', 'TEST', 'COMPLETE', 'DELIVER', 'done', 'CANCEL'] and self.process_type == 'pickup':
            raise Warning(
                "You can't change the status to done untill the Repair order is in Pickup state")
        elif self.order_id.state in ['QUOTE', 'APPROVE', 'PARTS', 'PICKUP', 'INSPECT', 'LIFT', 'TEST', 'COMPLETE', 'CANCEL'] and self.process_type == 'delivery':
            raise Warning(
                "You can't change the status to done untill the Repair order is completed")
        if self.order_id.state == 'PICKUP':
            self.order_id.write(
                {'state': 'INSPECT', 'pickup_date': datetime.datetime.now()})
        elif self.order_id.state == 'DELIVER':
            self.order_id.write(
                {'state': 'done', 'deliver_date': datetime.datetime.now()})
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        if self.process_type == 'pickup':
            self.order_id.write({'pickup': False})
        if self.process_type == 'delivery':
            self.order_id.write({'delivery': False})

        mail_values = {
            'email_from': 'admin@noblerush.com',
            'email_to': self.partner_id.email,
            'subject': 'Cancel Pickup and Delivery',
            'body_html': '<h2>Hi %s,</h2><h3>Your Service Ride Pickup has been Successfully Cancelled at %s</h3>' % (self.partner_id.name, self.date_planned_start),
            'notification': True,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
        self.write({'state': 'cancel'})
