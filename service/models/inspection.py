#    Techspawn Solutions Pvt. Ltd.
#    Copyright (C) 2016-TODAY Techspawn(<http://www.Techspawn.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import datetime
import logging
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import odoo.addons.decimal_precision as dp


class VehicleImages(models.Model):

    """ Vehicle images model """
    _name = 'inspection.images'
    _description = 'images of the vehicles before starting the service are stored here'
    image = fields.Binary(string="Image")
    name = fields.Char(string="Name")
    description = fields.Text(string="Description")

    service_id = fields.Many2one(comodel_name='service.inspection',
                                 string='Service Image')


class ServiceInspection(models.Model):

    """ Service inspection module"""
    _name = "service.inspection"

    name = fields.Char("Inspection Name", compute='_compute_inspection_name', states={
                       'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer Name',
        readonly=False,
        required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
    )

    date = fields.Date(string="Date", default=fields.Datetime.now, states={
                       'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    repair_order_id = fields.Many2one(comodel_name='service.repair_order',
                                      string='Repair Order',
                                      readonly=False,
                                      required=True,
                                      domain="[('state', 'not in', ('QUOTE','APPROVE','PARTS','PICKUP','LIFT','TEST','COMPLETE','DELIVER','done','CANCEL'))]",
                                      states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    major_unit_id = fields.Many2one(comodel_name='major_unit.major_unit',
                                    string='Vehicle',
                                    domain="[('partner_id', '=', partner_id)]",
                                    readonly=False,
                                    required=True,
                                    states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    service_advisor_id = fields.Many2one(comodel_name='hr.employee',
                                         string="Service Advisor",
                                         readonly=False,
                                         required=False,
                                         states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    technician_id = fields.Many2one(comodel_name='hr.employee',
                                    string="Technician",
                                    readonly=False,
                                    required=False,
                                    states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    date_promised = fields.Datetime(string="Date Promised", states={
                                    'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    year = fields.Char(string="Year", states={
                       'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    make = fields.Char(string="Make", states={
                       'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    models = fields.Char(string="Models", states={
                         'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    licence_number = fields.Char(string="Licence Number", states={
                                 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    vin = fields.Char(string="VIN", states={
                      'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    mileage = fields.Char(string="Mileage", states={
                          'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    color = fields.Char(string="Color", states={
                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    battery = fields.Char(string="Battery", states={
                          'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    brake_thickness = fields.Char(string="Brake Disk Thickness", states={
                                  'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    brake = fields.Char(string="Brake", states={
                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    carbs = fields.Char(string="Carbs/Throttle Bodies",
                        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    chain = fields.Char(string="ChainSprockets", states={
                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    charging_system = fields.Char(string="Charging System", states={
                                  'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    clutch = fields.Char(string="Clutch", states={
                         'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    control = fields.Char(
        string="Control/Cable", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    cooling_system = fields.Char(string="Cooling System", states={
                                 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    engine_oil = fields.Char(string="Engine Oil", states={
                             'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    exhaust_system = fields.Char(string="Exhaust System", states={
                                 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    final_drive = fields.Char(string="Final Drive", states={
                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    fuel_line = fields.Char(string="Fuel Lines", states={
                            'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    headlight = fields.Char(string="HeadLight", states={
                            'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    hydraulic_fluid = fields.Char(string="Hydraulic Fluids", states={
                                  'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    iginition_system = fields.Char(string="Iginition System", states={
                                   'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    instruments = fields.Char(string="Instructions", states={
                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    oil_leak = fields.Char(string="Oil Leak", states={
                           'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    pivot_bearing = fields.Char(string="Pivot Bearing", states={
                                'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    stand = fields.Char(string="Side/Center Stand",
                        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    sight_glass = fields.Char(string="Sight Glass", states={
                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    starter = fields.Char(string="Starter", states={
                          'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    steering_dumpener = fields.Char(string="Steering Dumpener", states={
                                    'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    steering_head_bearing = fields.Char(string="Steering Head Bearing", states={
                                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    taillight = fields.Char(string="TailLight/BreakLight",
                            states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    throttle_action = fields.Char(string="Throttle Action", states={
                                  'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    tires = fields.Char(string="Tires", states={
                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    transmission = fields.Char(string="Transmission", states={
                               'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    tune = fields.Char(string="Tune/Compression",
                       states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    turn_signal = fields.Char(string="Turn Signals", states={
                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    battery_inspection = fields.Boolean(string="Inspected", default=False, states={
                                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    brake_thickness_inspection = fields.Boolean(string="Inspected", default=False, states={
                                                'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    brake_inspection = fields.Boolean(string="Inspected", default=False, states={
                                      'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    carbs_inspection = fields.Boolean(string="Inspected", default=False, states={
                                      'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    chain_inspection = fields.Boolean(string="Inspected", default=False, states={
                                      'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    charging_system_inspection = fields.Boolean(string="Inspected", default=False, states={
                                                'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    clutch_inspection = fields.Boolean(string="Inspected", default=False, states={
                                       'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    control_inspection = fields.Boolean(string="Inspected", default=False, states={
                                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    cooling_system_inspection = fields.Boolean(string="Inspected", default=False, states={
                                               'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    engine_oil_inspection = fields.Boolean(string="Inspected", default=False, states={
                                           'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    exhaust_system_inspection = fields.Boolean(string="Inspected", default=False, states={
                                               'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    final_drive_inspection = fields.Boolean(string="Inspected", default=False, states={
                                            'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    fuel_line_inspection = fields.Boolean(string="Inspected", default=False, states={
                                          'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    headlight_inspection = fields.Boolean(string="Inspected", default=False, states={
                                          'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    hydraulic_fluid_inspection = fields.Boolean(string="Inspected", default=False, states={
                                                'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    iginition_system_inspection = fields.Boolean(string="Inspected", default=False, states={
                                                 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    instruments_inspection = fields.Boolean(string="Inspected", default=False, states={
                                            'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    oil_leak_inspection = fields.Boolean(string="Inspected", default=False, states={
                                         'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    pivot_bearing_inspection = fields.Boolean(string="Inspected", default=False, states={
                                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    stand_inspection = fields.Boolean(string="Inspected", default=False, states={
                                      'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    sight_glass_inspection = fields.Boolean(string="Inspected", default=False, states={
                                            'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    starter_inspection = fields.Boolean(string="Inspected", default=False, states={
                                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    steering_dumpener_inspection = fields.Boolean(string="Inspected", default=False, states={
                                                  'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    steering_head_bearing_inspection = fields.Boolean(string="Inspected", default=False, states={
                                                      'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    taillight_inspection = fields.Boolean(string="Inspected", default=False, states={
                                          'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    throttle_action_inspection = fields.Boolean(string="Inspected", default=False, states={
                                                'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    tires_inspection = fields.Boolean(string="Inspected", default=False, states={
                                      'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    transmission_inspection = fields.Boolean(string="Inspected", default=False, states={
                                             'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    tune_inspection = fields.Boolean(string="Inspected", default=False, states={
                                     'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    turn_signal_inspection = fields.Boolean(string="Inspected", default=False, states={
                                            'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    battery_approved = fields.Boolean(string="Approved", default=False, states={
                                      'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    brake_thickness_approved = fields.Boolean(string="Approved", default=False, states={
                                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    brake_approved = fields.Boolean(string="Approved", default=False, states={
                                    'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    carbs_approved = fields.Boolean(string="Approved", default=False, states={
                                    'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    chain_approved = fields.Boolean(string="Approved", default=False, states={
                                    'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    charging_system_approved = fields.Boolean(string="Approved", default=False, states={
                                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    clutch_approved = fields.Boolean(string="Approved", default=False, states={
                                     'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    control_approved = fields.Boolean(string="Approved", default=False, states={
                                      'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    cooling_system_approved = fields.Boolean(string="Approved", default=False, states={
                                             'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    engine_oil_approved = fields.Boolean(string="Approved", default=False, states={
                                         'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    exhaust_system_approved = fields.Boolean(string="Approved", default=False, states={
                                             'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    final_drive_approved = fields.Boolean(string="Approved", default=False, states={
                                          'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    fuel_line_approved = fields.Boolean(string="Approved", default=False, states={
                                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    headlight_approved = fields.Boolean(string="Approved", default=False, states={
                                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    hydraulic_fluid_approved = fields.Boolean(string="Approved", default=False, states={
                                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    iginition_system_approved = fields.Boolean(string="Approved", default=False, states={
                                               'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    instruments_approved = fields.Boolean(string="Approved", default=False, states={
                                          'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    oil_leak_approved = fields.Boolean(string="Approved", default=False, states={
                                       'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    pivot_bearing_approved = fields.Boolean(string="Approved", default=False, states={
                                            'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    stand_approved = fields.Boolean(string="Approved", default=False, states={
                                    'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    sight_glass_approved = fields.Boolean(string="Approved", default=False, states={
                                          'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    starter_approved = fields.Boolean(string="Approved", default=False, states={
                                      'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    steering_dumpener_approved = fields.Boolean(string="Approved", default=False, states={
                                                'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    steering_head_bearing_approved = fields.Boolean(string="Approved", default=False, states={
                                                    'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    taillight_approved = fields.Boolean(string="Approved", default=False, states={
                                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    throttle_action_approved = fields.Boolean(string="Approved", default=False, states={
                                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    tires_approved = fields.Boolean(string="Approved", default=False, states={
                                    'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    transmission_approved = fields.Boolean(string="Approved", default=False, states={
                                           'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    tune_approved = fields.Boolean(string="Approved", default=False, states={
                                   'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    turn_signal_approved = fields.Boolean(string="Approved", default=False, states={
                                          'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    miscellaneous = fields.Char(string="Miscellaneous", states={
                                'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    miscellaneous_inspection = fields.Boolean(string="Inspected", default=False, states={
                                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    miscellaneous_approved = fields.Boolean(string="Approved", default=False, states={
                                            'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    notes = fields.Text(string="Notes", states={
                        'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    standard_job_ids = fields.One2many('service.suggested.standard_job',
                                       'inspection_id',
                                       string='Suggested Jobs',
                                       states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    amount_untaxed = fields.Float(string='Untaxed Amount',
                                  store=True,
                                  readonly=True,
                                  compute='_compute_amount_all',
                                  digits=dp.get_precision('Product Price'))

    amount_tax = fields.Float(string='Taxes',
                              store=True,
                              readonly=True,
                              compute='_compute_amount_all',
                              digits=dp.get_precision('Product Price'))

    amount_total = fields.Float(string='Total',
                                store=True,
                                readonly=True,
                                compute='_compute_amount_all',
                                digits=dp.get_precision('Product Price'))
    vehicle_service_image = fields.One2many(comodel_name='inspection.images',
                                            inverse_name='service_id',
                                            string='Customer Vehicles Ride Images',
                                            required=False,
                                            )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Progress'),
        ('done', 'Finished'),
        ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.onchange('repair_order_id')
    def on_change_repair_order(self):
        self.partner_id = self.repair_order_id.partner_id.id
        self.major_unit_id = self.repair_order_id.major_unit_id.id
        self.vin = self.major_unit_id.vin_sn
        self.mileage = self.major_unit_id.mileage
        for attributes in self.repair_order_id.major_unit_id.attribute_value_ids:
            if attributes.attribute_id.name.lower() == 'make':
                self.make = attributes.name
            elif attributes.attribute_id.name.lower() == 'year':
                self.year = attributes.name
            elif attributes.attribute_id.name.lower() == 'mileage':
                self.mileage = attributes.name
            elif attributes.attribute_id.name.lower() == 'color':
                self.color = attributes.name
            elif attributes.attribute_id.name.lower() == 'model':
                self.models = attributes.name
            elif self.repair_order_id.licence_no:
                self.licence_number = self.repair_order_id.licence_no

    @api.multi
    @api.depends('repair_order_id')
    def _compute_inspection_name(self):
        for inspection in self:
            inspection.name = 'RO ' + \
                inspection.repair_order_id.name + ' Inspection'

    @api.multi
    def action_inspect_confirm(self):
        if self.state == 'draft':
            self.write({'state': 'progress'})

    @api.multi
    def action_inspect_progress(self):
        if self.repair_order_id.state in ['QUOTE', 'APPROVE', 'PARTS', 'PICKUP', 'LIFT', 'TEST', 'COMPLETE', 'DELIVER', 'done', 'CANCEL'] and self.repair_order_id.product_pickup_ids.process_type == 'pickup':
            raise Warning(
                "You can't change the status to done untill the Repair order is in Inspect State")
        if self.repair_order_id.state == 'INSPECT' and self.state in ['progress']:
            if self.standard_job_ids:
                repair_order_status = 'QUOTE'
            else:
                repair_order_status = 'LIFT'
            self.repair_order_id.write({'state': repair_order_status,
                                        'inspect_date': datetime.datetime.now()})
        mail_values = {
            'email_from': 'admin@noblerush.com',
            'email_to': self.partner_id.email,
            'subject': 'Inspection Done',
            'body_html': '<h2>Hi %s,</h2><h3>Your ride %s has been successfully passed inspection at %s</h3>' % (self.partner_id.name, self.major_unit_id.name, self.date_promised),
            'notification': True,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
        self.write({'state': 'done'})
        '''
        Redirect to Repair order window
        '''
        repair_order = self.mapped('repair_order_id')
        action = self.env.ref('service.service_action').read()[0]
        if self.state == 'done':
            action['views'] = [
                (self.env.ref('service.view_service_form').id, 'form')]
            action['res_id'] = repair_order.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_cancel(self):
        self.repair_order_id.write({'inspection': False})
        self.write({'state': 'cancel'})

    @api.model
    def default_get(self, fields):
        mechanic = []
        res = super(ServiceInspection, self).default_get(fields)
        if not res.get('partner_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'service.repair_order' and self.env.context.get('active_id'):
            temp = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1)
            res['partner_id'] = temp.partner_id.id
            res['major_unit_id'] = temp.major_unit_id.id
            res['repair_order_id'] = temp.id
            for mechanics in temp.mechanic_id:
                mechanic.append(mechanics.id)
            if 'technician_id' in self.env.context.keys():
                res['technician_id'] = self.env.context.get('technician_id')
        return res

    # @api.multi
    # @api.depends('repair_order_id')
    # def vehicle_detail(self):
    #     self.major_unit_id = self.repair_order_id.major_unit_id.id
    #     self.vin = self.major_unit_id.vin_sn
    #     # self.licence_number = self.major_unit_id.licence_no
    #     # self.mileage = self.major_unit_id.mileage
    #     # self.color = self.major_unit_id.color

    @api.model
    def create(self, vals):
        previous_inspection = self.env['service.inspection'].search(
            [('repair_order_id', '=', vals['repair_order_id'])])
        for inspect_order in previous_inspection:
            if inspect_order.state != 'cancel':
                temp = "Inspection already requested for " + \
                    str(inspect_order.repair_order_id.name)
                raise Warning(temp)

        res = super(ServiceInspection, self).default_get(vals)
        repair_order = self.env['service.repair_order'].search(
            [('id', '=',  vals['repair_order_id'])], limit=1)

        vals['partner_id'] = repair_order.partner_id.id
        vals['major_unit_id'] = repair_order.major_unit_id.id
        repair_order.write({'inspection': True})
        return super(ServiceInspection, self).create(vals)
