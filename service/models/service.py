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


import hashlib
import itertools
import mimetypes
import os
import re
from collections import defaultdict
import datetime
import logging
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import AccessError
from odoo.tools import config, human_size, ustr, html_escape
from odoo.tools.mimetypes import guess_mimetype

_logger = logging.getLogger(__name__)


class Skills(models.Model):
    _name = 'hr.skills'
    name = fields.Char(string="Skills")


class EmployeeLevel(models.Model):
    _name = 'hr.level'
    name = fields.Char(string="Employee Level")


class SaleOrder(models.Model):

    """ Mechanic Skills model"""
    _inherit = 'sale.order'
    service_id = fields.Many2one(comodel_name='service.repair_order',
                                 string="Services"
                                 )


class MechanicSkills(models.Model):

    """ Mechanic Skills model"""
    _inherit = 'hr.employee'
    info = fields.Text(string="Info of skills")
    efficiency = fields.Char(string="Efficiency")
    level = fields.Many2one(comodel_name='hr.level',
                            string="Employee Level"
                            )
    date_planned_start = fields.Datetime(
        'Deadline Start', copy=False, default=fields.Datetime.now,
        index=True, required=True,
        oldname="date_planned")

    # date_planned_start = fields.Datetime(
    #     'Deadline Start', copy=False, default=fields.Datetime.now,
    #     index=True, required=True,
    #     oldname="date_planned")

    skills = fields.Many2many(comodel_name='hr.skills', string="Skills")


class Customers(models.Model):

    """Custom fields for Customers"""
    _inherit = 'res.partner'
    customer_ride_service = fields.One2many(
        comodel_name='service.repair_order',
        inverse_name='partner_id',
        string='Customer Vehicles Ride services',
        readonly=False,
        required=False,
    )

    customer_product_ids = fields.One2many(
        comodel_name='sale.order',
        inverse_name='partner_id',
        string='Customer Products',
        readonly=False,
        required=False,
    )

    @api.multi
    def unlink(self):
        for partner in self:
            child_ids = partner.child_ids
            for child in child_ids:
                child.unlink()
            super(Customers, partner).unlink()


class Documents(models.Model):
    _name = 'repair.documents'

    @api.model
    def _storage(self):
        return self.env['ir.config_parameter'].sudo().get_param('ir_attachment.location', 'file')

    def _mark_for_gc(self, fname):
        """ Add ``fname`` in a checklist for the filestore garbage collection. """
        # we use a spooldir: add an empty file in the subdirectory 'checklist'
        full_path = os.path.join(self._full_path('checklist'), fname)
        if not os.path.exists(full_path):
            dirname = os.path.dirname(full_path)
            if not os.path.isdir(dirname):
                with tools.ignore(OSError):
                    os.makedirs(dirname)
            open(full_path, 'ab').close()

    @api.model
    def _file_delete(self, fname):
        # simply add fname to checklist, it will be garbage-collected later
        self._mark_for_gc(fname)

    @api.model
    def _filestore(self):
        return config.filestore(self._cr.dbname)

    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for attachment in self:
            if attachment.res_model and attachment.res_id:
                record = self.env[attachment.res_model].browse(
                    attachment.res_id)
                attachment.res_name = record.display_name

    @api.model
    def _file_read(self, fname, bin_size=False):
        full_path = self._full_path(fname)
        r = ''
        try:
            if bin_size:
                r = human_size(os.path.getsize(full_path))
            else:
                r = open(full_path, 'rb').read().encode('base64')
        except (IOError, OSError):
            _logger.info("_read_file reading %s", full_path, exc_info=True)
        return r

    @api.depends('store_fname', 'db_datas')
    def _compute_datas(self):
        bin_size = self._context.get('bin_size')
        for attach in self:
            if attach.store_fname:
                attach.datas = self._file_read(attach.store_fname, bin_size)
            else:
                attach.datas = attach.db_datas

    @api.model
    def _full_path(self, path):
        # sanitize path
        path = re.sub('[.]', '', path)
        path = path.strip('/\\')
        return os.path.join(self._filestore(), path)

    @api.model
    def _get_path(self, bin_data, sha):
        # retro compatibility
        fname = sha[:3] + '/' + sha
        full_path = self._full_path(fname)
        if os.path.isfile(full_path):
            return fname, full_path        # keep existing path

        # scatter files across 256 dirs
        # we use '/' in the db (even on windows)
        fname = sha[:2] + '/' + sha
        full_path = self._full_path(fname)
        dirname = os.path.dirname(full_path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return fname, full_path

    @api.model
    def _file_write(self, value, checksum):
        bin_value = value.decode('base64')
        fname, full_path = self._get_path(bin_value, checksum)
        if not os.path.exists(full_path):
            try:
                with open(full_path, 'wb') as fp:
                    fp.write(bin_value)
                # add fname to checklist, in case the transaction aborts
                self._mark_for_gc(fname)
            except IOError:
                _logger.info("_file_write writing %s",
                             full_path, exc_info=True)
        return fname

    def _inverse_datas(self):
        location = self._storage()
        for attach in self:
            # compute the fields that depend on datas
            value = attach.datas
            bin_data = value and value.decode('base64') or ''
            vals = {
                'file_size': len(bin_data),
                'checksum': self._compute_checksum(bin_data),
                'index_content': self._index(bin_data, attach.datas_fname, attach.mimetype),
                'store_fname': False,
                'db_datas': value,
            }
            if value and location != 'db':
                # save it to the filestore
                vals['store_fname'] = self._file_write(value, vals['checksum'])
                vals['db_datas'] = False

            # take current location in filestore to possibly garbage-collect it
            fname = attach.store_fname
            # write as superuser, as user probably does not have write access
            super(Documents, attach.sudo()).write(vals)
            if fname:
                self._file_delete(fname)

    def _compute_checksum(self, bin_data):
        """ compute the checksum for the given datas
            :param bin_data : datas in its binary form
        """
        # an empty file has a checksum too (for caching)
        return hashlib.sha1(bin_data or '').hexdigest()

    @api.model
    def _index(self, bin_data, datas_fname, file_type):
        """ compute the index content of the given filename, or binary data.
            This is a python implementation of the unix command 'strings'.
            :param bin_data : datas in binary form
            :return index_content : string containing all the printable character of the binary data
        """
        index_content = False
        if file_type:
            index_content = file_type.split('/')[0]
            if index_content == 'text':  # compute index_content only for text type
                words = re.findall("[^\x00-\x1F\x7F-\xFF]{4,}", bin_data)
                index_content = ustr("\n".join(words))
        return index_content

    name = fields.Char('Attachment Name', required=True)
    datas_fname = fields.Char('File Name')
    description = fields.Text('Description')
    res_name = fields.Char(
        'Resource Name', compute='_compute_res_name', store=True)
    res_model = fields.Char('Resource Model',
                            help="The database object this attachment will be attached to.")
    res_field = fields.Char('Resource Field',)
    res_id = fields.Integer('Resource ID',
                            help="The record id this is attached to.")
    create_date = fields.Datetime('Date Created', )
    type = fields.Selection([('url', 'URL'), ('binary', 'File')],
                            string='Type', required=True, default='binary', change_default=True,
                            help="You can either upload a file from your computer or copy/paste an internet link to your file.")
    url = fields.Char('Url', index=True, size=1024)
    public = fields.Boolean('Is public document')

    # the field 'datas' is computed and may use the other fields below
    datas = fields.Binary(string='File Content',
                          compute='_compute_datas', inverse='_inverse_datas')
    db_datas = fields.Binary('Database Data')
    store_fname = fields.Char('Stored Filename')
    file_size = fields.Integer('File Size', readonly=True)
    checksum = fields.Char("Checksum/SHA1", size=40, index=True, )
    mimetype = fields.Char('Mime Type')
    index_content = fields.Text(
        'Indexed Content',  prefetch=False)
    repair_id = fields.Many2one('service.repair_order', string="Repair Order")


class VehicleService(models.Model):

    """Vehicle Service Detail"""
    _inherit = 'service.repair_order'
    _description = "Vehicle Service Detail"

    warranty = fields.Boolean(string="Warranty",
                              help="Service vehicle warranty",
                              states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    loaner = fields.Boolean(string="Loaner Bikes Required")

    loaner_product_id = fields.Many2one('product.product',
                                        string="Loaner Bikes",
                                        required=False,)

    licence_no = fields.Char(string="Licence No", states={
                             'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    quote_date = fields.Datetime('Quoted Date')
    approve_date = fields.Datetime('Approved Date')
    confirm_date = fields.Datetime('Confirm Date', default=None)
    reconfirm_date = fields.Datetime('Re-confirm Date')
    parts_date = fields.Datetime('Parts Arrived Date')
    pickup_date = fields.Datetime('Pickup Date')
    inspect_date = fields.Datetime('Inspected Date')
    lift_date = fields.Datetime('Lift Date')
    test_date = fields.Datetime('Tested Date')
    complete_date = fields.Datetime('Completed Date')
    deliver_date = fields.Datetime('Delivered Date')
    # comeback_date = fields.Datetime('Comeback Date')
    done_date = fields.Datetime('Done Date')
    cancel_date = fields.Datetime('Canceled Date')

    state = fields.Selection([('QUOTE', 'Quote'),
                              ('APPROVE', 'Approve'),
                              ('PARTS', 'Parts'),
                              ('PICKUP', 'Pickup'),
                              ('INSPECT', 'Inspect'),
                              ('LIFT', 'Lift'),
                              ('TEST', 'Test'),
                              ('COMPLETE', 'Complete'),
                              ('DELIVER', 'Deliver'),
                              ('done', 'Done'),
                              ('CANCEL', 'Cancel'),
                              ],
                             copy=False,
                             track_visibility='onchange',
                             string='State',
                             required=True,
                             select=True,
                             default="QUOTE",
                             states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    requested_date = fields.Date("Repair Order Date",
                                 required=True,
                                 default=fields.Date.today(),
                                 states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    start_date = fields.Datetime("Start Date",
                                 required=True,
                                 default=fields.Datetime.now(),
                                 states={'done': [('readonly', True)],
                                         'CANCEL': [('readonly', True)]})

    end_date = fields.Datetime("Due Date",
                               states={'done': [('readonly', True)],
                                       'CANCEL': [('readonly', True)]})

    pickup_time = fields.Datetime(compute='_compute_pickup_delivery',
                                  string="Pickup Time",
                                  store=True,
                                  states={'done': [('readonly', True)],
                                          'CANCEL': [('readonly', True)]})
    pickup_address = fields.Text(compute='_compute_pickup_delivery',
                                 string="Pickup Address",
                                 states={'done': [('readonly', True)],
                                         'CANCEL': [('readonly', True)]})

    delivery_time = fields.Datetime(compute='_compute_pickup_delivery',
                                    string="Delivery Time",
                                    states={'done': [('readonly', True)],
                                            'CANCEL': [('readonly', True)]})
    delivery_address = fields.Text(compute='_compute_pickup_delivery',
                                   string="Delivery Address",
                                   states={'done': [('readonly', True)],
                                           'CANCEL': [('readonly', True)]})

    urgency = fields.Selection([('0', 'Low'),
                                ('1', 'Medium'),
                                ('2', 'High'),
                                ('3', 'Highest')],
                               String='Priority',
                               required=True,
                               default='1',
                               states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    repair_type = fields.Selection([('repair_order', 'Repair Order'),
                                    ('pdi', 'Internal'),
                                    ('comeback', 'Comeback')
                                    ],
                                   String='Priority',
                                   required=True,
                                   states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    pickup = fields.Boolean(default=False,
                            string="Pickup Required",
                            states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    delivery = fields.Boolean(default=False,
                              string="Delivery Required",
                              states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    problem_description = fields.Text(string="Problem Description",
                                      states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    mechanic_id = fields.Many2one(comodel_name='hr.employee',
                                  string='Mechanic',
                                  readonly=False,
                                  required=False,
                                  states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    mechanic_skill = fields.Many2many(comodel_name='hr.skills',
                                      string='Mechanic Service Skills',
                                      readonly=False,
                                      required=False,
                                      states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    failure_date = fields.Date(string="Failure Date", states={
                               'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    claim_id = fields.Char(string="Claim Id", states={
                           'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    claim_date = fields.Date(string="Claim Date", states={
                             'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    manufacturer = fields.Char(string="Manufacturer", states={
                               'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    warranty_type = fields.Char(string="Warranty Type", states={
                                'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    defect_type = fields.Char(string="Defect Type", states={
                              'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    defect_group = fields.Char(string="Defect Group", states={
                               'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    defect_code = fields.Char(string="Defect Code", states={
                              'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    complaint = fields.Text(string="Complaint", states={
                            'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    cause = fields.Text(string="Cause", states={
                        'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    correction = fields.Text(string="Correction", states={
                             'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    vehicle_service_image = fields.One2many(comodel_name='vehicle.images',
                                            inverse_name='service_id',
                                            string='Customer Vehicles Ride Images',
                                            required=False,
                                            states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    company_id = fields.Many2one('res.company',
                                 'Company',
                                 default=lambda self: self.env[
                                     'res.company']._company_default_get('sale.order'),
                                 states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})
    user_id = fields.Many2one('res.users',
                              string='Salesperson',
                              index=True,
                              track_visibility='onchange',
                              default=lambda self: self.env.user,
                              states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 )
    document = fields.One2many('repair.documents', 'repair_id', string="Documents", states={
        'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    product_inspection_ids = fields.One2many('service.inspection',
                                             'repair_order_id',
                                             required=False,
                                             states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    inspection_variant_count = fields.Integer('# Product Variants',
                                              compute='_compute_inspection_variant_count',
                                              states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    inspection = fields.Boolean(default=False,
                                string="Inspection",
                                states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    pricelist_id = fields.Many2one('product.pricelist',
                                   string='Pricelist',
                                   required=False,
                                   readonly=True,
                                   states={
                                       'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                   help="Pricelist for current sales order.")

    currency_id = fields.Many2one("res.currency",
                                  related='pricelist_id.currency_id',
                                  string="Currency",
                                  readonly=True,
                                  required=False,
                                  states={'done': [('readonly', True)], 'CANCEL': [('readonly', True)]})

    qty_bool = fields.Boolean("Quantity Available")

    major_unit_id = fields.Many2one(
        'major_unit.major_unit', string='Vehicle', required=True, ondelete='cascade')

    sign_date = fields.Datetime(
        string="Signature Date", default=fields.Datetime.now())
    terms_condition = fields.Text(
        string="Terms and Condition", default='This is a default text for terms and condition so please accept it')

    miles_in = fields.Char(string="Miles IN")
    miles_out = fields.Char(string="Miles OUT")
    plate = fields.Char(string="Vehicle Number Plate",
                        compute="_compute_vehicle_plate")

    @api.multi
    def _compute_vehicle_plate(self):
        self.plate = self.major_unit_id.vehicle_number_plate

    @api.multi
    def _compute_pickup_delivery(self):
        for orders in self:
            for order in orders.product_pickup_ids:
                if order.process_type == 'pickup' and order.state not in ['cancel']:
                    self.pickup_time = order.date_planned_start
                    self.write({'pickup': True})
                    street1 = order.street or ''
                    street2 = order.street2 or ''
                    zip = order.zip or ''
                    city = order.city or ''
                    state = order.state_id.name or ''
                    country = order.country_id.name or ''
                    self.pickup_address = street1 + '\n' + street2 + '\n' + \
                        zip + '\n' + city + '\n' + state + '\n' + country
                elif order.process_type == 'delivery' and order.state not in ['cancel']:
                    self.delivery_time = order.date_planned_start
                    self.write({'delivery': True})
                    street1 = order.street or ''
                    street2 = order.street2 or ''
                    zip = order.zip or ''
                    city = order.city or ''
                    state = order.state_id.name or ''
                    country = order.country_id.name or ''
                    self.delivery_address = street1 + '\n' + street2 + '\n' + \
                        zip + '\n' + city + '\n' + state + '\n' + country
    


    @api.multi
    def write(self, vals):
        service = super(VehicleService, self).write(vals)
        if 'state' in vals.keys():
            alert_values = {
                'backend_id': [[6, 0, self.backend_id.ids]],
                'customer_id': self.partner_id.id,
                'state_type': self.state,
                'email': self.major_unit_id.cr_store_id.email,
                # 'logo_image':  self.major_unit_id.prod_lot_id.get_current_location().company_id.logo,
                'name': 'SERVICE REMINDER ',
                'description': 'Hi %s,Welcome again to the %s Family .'
                'This is just a helpful reminder to schedule your service. '
                'The service should happen at 600 miles or Six months. If you have already had your service, congrats !! Properly maintaining your %s at the factory specified intervals is required to keep your warranty valid.  Your Service Status is %s'
                % (self.partner_id.name, self.major_unit_id[0].make, self.major_unit_id.name, self.state),
                'phone': self.major_unit_id.cr_store_id.phone,
                'store_name': self.major_unit_id.cr_store_id.name,
                'major_unit_id': self.major_unit_id.id,
            }
            alert = self.env['service.messanger'].create(alert_values)
            alert.sync_service_messanger()

            email_template_obj = self.env['mail.template']
            template_ids = self.env['ir.model.data'].get_object_reference(
            'service', 'send_service_status')[1]
            email_template = email_template_obj.search([('id', '=', template_ids)])
            if email_template:
                vals = email_template.generate_email(self.id)
                vals['email_to'] = self.major_unit_id.partner_id.email
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(vals)
                if msg_id:
                    msg_id.send([msg_id])

        return service

    @api.multi
    def action_cancel(self):

        self.action_undo()
        drm_work_order_obj=self.env['drm.workorders']
        work_order_cancel_obj=drm_work_order_obj.search(
            [('repair_order_id', '=', self.id)])
        work_order_cancel_obj.write({'state': 'cancel'})

        self.write({'state': 'CANCEL', 'cancel_date': datetime.datetime.now()})

    def action_check_available(self):
        for product_line in self.product_ids:
            if product_line.qty_available < product_line.quantity:
                qty_bool = False
                purchase=self.env['purchase.order.line'].search([('product_id','=',product_line.product_id.id),('state','not in',['purchase','done'])])
                if purchase:
                    raise Warning('Please Check for the product stock its LOW. Purchase order has been placed!!!')
                elif not purchase and self.env['product.template'].search([('id','=',product_line.product_id.product_tmpl_id.id)]).type!='service':
                    product= self.env['product.template'].search([('id','=',product_line.product_id.product_tmpl_id.id)])
                    seller=product.seller_ids
                    if not seller:
                        raise Warning('Please add vendor to part/labor product')
                    vendors=[{s.name.id:s['price'] for s in seller}]
                    quant=[{s.name.id:s['min_qty'] for s in seller}]
                    uom=[{s.name.id:s.product_uom.id for s in seller}]
                    vendor=min(vendors[0],key=vendors[0].get)
                    values={'partner_id':vendor,'date_order':datetime.datetime.now(),'order_line':[(0,0,{'product_id':product_line.product_id.id,'name':product_line.product_id.name,'date_planned':datetime.datetime.now(),'product_qty':quant[0][vendor],'price_unit':vendors[0][vendor],'taxes_id':product_line.product_id.supplier_taxes_id,'product_uom':uom[0][vendor]})]}
                    self.env['purchase.order'].create(values)
            else:
                qty_bool = True
                # stock_quant=self.env['stock.quant'].search([('product_id','=',product_line.product_id.product_tmpl_id.id)])
                # quan=stock_quant.qty-product_line.quantity
                # stock_quant.write({'qty':quan})
        self.write({'state': 'PARTS', 'parts_date': datetime.datetime.now()})

    @api.multi
    def action_confirm_parts(self):
        if self.pickup_date and not self.inspect_date:
            self.write({'state': 'INSPECT',
                        'inspect_date': datetime.datetime.now()})
        elif self.pickup_date and self.inspect_date:
            self.write({'state': 'LIFT',
                        'lift_date': datetime.datetime.now()})
        else:
            self.write({'state': 'PICKUP',
                        'parts_date': datetime.datetime.now()})

    @api.multi
    def action_confirm_pickup(self):
        if self.repair_type == "repair_order" or self.repair_type == "comeback":
            self.write(
                {'state': 'INSPECT', 'pickup_date': datetime.datetime.now()})
        elif self.repair_type == "pdi":
            self.write(
                {'state': 'LIFT', 'pickup_date': datetime.datetime.now()})

    @api.multi
    def action_confirm_sale(self):
        years = 0
        for attribute in self.major_unit_id.attribute_value_ids:
            if attribute.attribute_id.name.lower() == 'years':
                years = 1

        if years or self.major_unit_id.year:
            is_year = True
        else:
            is_year = False

        if self.product_ids and is_year and self.major_unit_id.model and self.partner_id.email:
            self.action_confirm()
            if self.repair_type == "repair_order":
                self.create_sale_order()
            self.create_new_workorder()
            if self.confirm_date:
                self.write({'state': 'APPROVE',
                            'reconfirm_date': datetime.datetime.now()})
            else:
                self.write({'state': 'APPROVE',
                            'confirm_date': datetime.datetime.now()})
        elif not self.product_ids:
            raise Warning('Please select atleast one Product to Confirm')
        elif not is_year:
            raise Warning('Please select Year of Vehicle from Product Variants')
        elif not self.major_unit_id.model:
            raise Warning('Please select Model of Vehicle from Product Variants')
        elif not self.partner_id.email:
            raise Warning('Please fill Email field of customer')

    @api.multi
    def action_confirm_delivery(self):
        self.write({'state': 'done',
                    'delivery_date': datetime.datetime.now(),
                    'done_date': datetime.datetime.now()})

    @api.multi
    def action_confirm_lift(self):
        self.write({'state': 'TEST', 'lift_date': datetime.datetime.now()})

    @api.multi
    def action_confirm_test(self):
        self.write({'state': 'COMPLETE', 'test_date': datetime.datetime.now()})

    @api.multi
    def action_confirm_complete(self):
        self.write({'state': 'DELIVER',
                    'complete_date': datetime.datetime.now()})

    def _prepare_sale_order_line(self):
        lines = []
        for product_line in self.product_ids:
            if product_line.state in ['confirm', 'cancel']:
                continue
            res = {
                'product_id': product_line.product_id.id,
                'product_uom': product_line.product_id.uom_id.id,
                'product_uom_qty': product_line.quantity,
                # 'price_unit' : line.price
            }
            lines.append([0, 0, res])
            product_line.write({'state': 'confirm'})
        return lines

    @api.multi
    def create_sale_order(self):
        sale_order_lines = self._prepare_sale_order_line()
        if sale_order_lines:
            if self.product_sale_order_ids:
                self.product_sale_order_ids[0].write(
                    {'order_line': sale_order_lines, })
            else:
                order_id = self.env['sale.order'].create({'service_id': self.id,
                                                          'order_line': [],
                                                          'picking_policy': 'direct',
                                                          'date_order': '2017-01-23 14:39:13',
                                                          'partner_id': self.partner_id.id,
                                                          'order_line': sale_order_lines,
                                                          })
                # order_id.action_confirm()

    def _prepare_workorders(self, job):
        res = {'standard_job_id': job.id,
               'name': job.name,
               'repair_order_id': self.id,
               'vehicle_id': self.major_unit_id.id,
               'mechanic_id': self.mechanic_id.id,
               'customer_id': self.partner_id.id,
               }
        return res

    def workorder_exist(self, job):

        for workorder in self.product_workorder_ids:
            if workorder.standard_job_id.id == job.id:
                return True
        return False

    @api.multi
    def create_new_workorder(self):
        for job in self.standard_job_ids:
            if self.workorder_exist(job):
                continue
            my_workorder_details = self.env['drm.workorders'].create(
                self._prepare_workorders(job))

    @api.one
    @api.depends('product_inspection_ids')
    def _compute_inspection_variant_count(self):
        self.inspection_variant_count = len(self.product_inspection_ids)

    product_sale_order_ids = fields.One2many('sale.order', 'service_id')
    product_sale_order_count = fields.Integer(
        '# Product Pickup', compute='_compute_sale_order_count')

    @api.one
    @api.depends('product_sale_order_ids')
    def _compute_sale_order_count(self):
        self.product_sale_order_count = len(self.product_sale_order_ids)

    product_pickup_ids = fields.One2many('drm.pickup', 'order_id')
    pickup_variant_count = fields.Integer(
        '# Product Pickup', compute='_compute_pickup_variant_count')

    @api.one
    @api.depends('product_pickup_ids')
    def _compute_pickup_variant_count(self):
        self.pickup_variant_count = len(self.product_pickup_ids)

    ###### create workorder count########
    product_workorder_ids = fields.One2many(
        'drm.workorders', 'repair_order_id')
    pickup_workorder_count = fields.Integer(
        '# Product Pickup', compute='_compute_workorder_variant_count')
    repair_workorder_done_count = fields.Integer(
        '# Done Work Orders', compute='_compute_workorder_done_count')

    @api.one
    @api.depends('product_workorder_ids')
    def _compute_workorder_variant_count(self):
        self.pickup_workorder_count = len(self.product_workorder_ids)

    @api.multi
    @api.depends('product_workorder_ids.state')
    def _compute_workorder_done_count(self):
        count = 0
        for orders in self.product_workorder_ids:
            if orders.state == 'done':
                count = count + 1
        self.repair_workorder_done_count = count

    ########### end #############

    @api.onchange('pickup')
    def _check_pickup(self):
        """ onchange module method on pickup field to add charges for pickup and delivery """
        if self.pickup == True:
            self.price = 10

    @api.model
    def create(self, vals):
        """ create a sequence for order number """
        if not vals.get('name', False):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'service.repair_order') or '/'
        vals['quote_date'] = datetime.datetime.now()
        """ Updated current part location in RO with respect to default location of the warehouse of standard job """
        if 'standard_job_ids' in vals.keys():
            standard = vals['standard_job_ids'][0][2]
            ware = self.env['service.standard_job'].search([('id','=',standard[0])]).warehouse
            loc = self.env['stock.warehouse'].search([('id','=',ware.id)])
            vals.update({'part_location_id': loc.lot_stock_id.id})
        return super(VehicleService, self).create(vals)

    @api.model
    def default_get(self, fields):
        """ 
        In this function partner_id is directly taken from customer 
        and added by default in form view
        """
        res = super(VehicleService, self).default_get(fields)
        if not res.get('partner_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'res.partner' and self.env.context.get('active_id'):
            res['partner_id'] = self.env['res.partner'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).id
        elif self.env.context.get('partner_id'):
            res['partner_id'] = self.env['res.partner'].search(
                [('id', '=', self.env.context['partner_id'])], limit=1).id
        if 'warranty' in self.env.context.keys():
            res['warranty'] = self.env.context.get('warranty')
        if 'default_repair_type' in self.env.context.keys():
            if res.get('repair_type')=='pdi':
                res['partner_id']=self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.id
        return res

    @api.multi
    def print_report(self):
        """ fn to print service order """
        return self.env['report'].get_action(self, 'report_service_order')

    @api.multi
    def action_view_sale_order(self):
        sale_orders = self.mapped('product_sale_order_ids')
        action = self.env.ref('sale.action_orders').read()[0]
        if len(sale_orders) > 1:
            action['domain'] = [('id', 'in', sale_orders.ids)]
        elif len(sale_orders) == 1:
            action['views'] = [
                (self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = sale_orders.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_inspect(self):

        inspections = self.mapped('product_inspection_ids')
        action = self.env.ref('service.service_inspections').read()[0]
        if len(inspections) > 1:
            action['domain'] = [('id', 'in', inspections.ids)]
        elif len(inspections) == 1:
            action['views'] = [
                (self.env.ref('service.view_service_inspection_form').id, 'form')]
            action['res_id'] = inspections.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_pickup(self):
        pickups = self.mapped('product_pickup_ids')
        action = self.env.ref('service.pickup_actions').read()[0]
        if len(pickups) > 1:
            action['domain'] = [('id', 'in', pickups.ids)]
        elif len(pickups) == 1:
            action['views'] = [
                (self.env.ref('service.view_pickup_form').id, 'form')]
            action['res_id'] = pickups.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_workorder(self):
        workorders = self.mapped('product_workorder_ids')

        action = self.env.ref('service.workorders_actions').read()[0]
        if len(workorders.ids) > 1:
            action['domain'] = [('id', 'in', workorders.ids)]
        elif len(workorders) == 1:
            action['views'] = [
                (self.env.ref('service.view_workorders_form').id, 'form')]
            action['res_id'] = workorders.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_quotation_send_mail(self, res_ids):
        """ Open a window to compose an email, pre-filled with the survey message """
        # Ensure that this survey has at least one page with at least one
        # question.

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'service', 'email_template_edi_service')[1]
        except ValueError:
            template_id = False

        compose_form_id = ir_model_data.get_object_reference(
            'mail', 'email_compose_message_wizard_form')[1]

        local_context = dict(
            default_model='service.repair_order',
            default_res_id=self.ids[0],
            default_use_template=bool(template_id),
            default_template_id=template_id,
            default_composition_mode='comment',
            mark_so_as_sent=True,
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': local_context,

        }

    @api.model
    def message_get_reply_to(self, res_ids, default=None):
        res = dict.fromkeys(res_ids, False)
        res.update(dict((res_id, default) for res_id in res_ids))
        return res


class VehicleServiceParts(models.Model):

    """Service Detail model"""
    _name = "service.repair_order.parts"
    _description = "Vehicle Service Parts Detail"

    service_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        readonly=False,
        required=True,
    )
    discount = fields.Float("Discount (%)")
    service_partner_id = fields.Many2one(comodel_name='res.partner',
                                         string='Customer',
                                         readonly=False,
                                         required=True,
                                         )
    state = fields.Selection([('requested', 'Requested'),
                              ('arrived', 'Arrived'),
                              ('canceled', 'Canceled'),
                              ],  string='State',
                             readonly=True,
                             required=True)
    requested_date = fields.Datetime("Scheduled Date")
    start_date = fields.Datetime("Start Date")


class VehicleImages(models.Model):

    """ Vehicle images model """
    _name = 'vehicle.images'
    _description = 'images of the vehicles before starting the service are stored here'
    image = fields.Binary(string="Image")
    name = fields.Char(string="Name")
    description = fields.Text(string="Description")

    service_id = fields.Many2one(comodel_name='service.repair_order',
                                 string='Service Image')



class notification(models.Model):
    _name = 'service.notification'

    customer_id = fields.Many2one(
       comodel_name='res.partner',
       string='Customer Name',
       readonly=False,
       required=True,
   )
    subject=fields.Char(string="Subject")
    description = fields.Text(string="Description")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email To")


    @api.onchange('customer_id')
    def on_change_workcenter(self):
        self.phone = self.customer_id.phone
        self.email = self.customer_id.email


    @api.multi
    def send_mail(self):
        mail_values = {
            'email_from': 'admin@noblerush.com',
            'email_to': self.customer_id.email,
            'subject': self.subject,
            'body_html': self.description,
            'notification': True,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
        raise Warning('Email Sent')