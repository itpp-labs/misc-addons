import logging
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class CustomerRides(models.Model):

    """Custom fields for Customers Rides"""
    _inherit = 'major_unit.major_unit'
    _description = "Vehicle Service Detail"
    image = fields.Binary('Image')
    # miles = fields.Char(string='Miles',
    #                     help='Number of miles last logged')
    # miles_date = fields.Date(string="Miles Date",
    #                          help='Date the miles were last logged')
    mileage = fields.Float(string='Mileage',
                           help='Vehicle mileage')
    vehical_registration_no = fields.Char(string='Vehicle Registration Number',
                                          related="vin_sn",
                                          help='Vehicle Registration Number')
    last_service = fields.Datetime("Last Serviced Date")
    purchase_date = fields.Date(string='Purchase Date',
                                help='Vehicle purchase date')
    interest_paid_to_date = fields.Date(string='Interest Paid to Date',
                                        help='How much interest has been paid to date on the bike with the floor plan lender')
    floor_plan_balance = fields.Date(string='Floor Plan Balance',
                                     help='How much debt is on the unit')
    repair_order = fields.Char(string='Repair Order',
                               help='Link to the Repair Order that relates to this particular Unit.')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        readonly=False,
        required=False,
    )
    cr_store_id = fields.Many2one(
        'res.company', string="Store Location")
    cr_sales_adviser = fields.Char(string="Sales Adviser")
    make = fields.Char(string="Make", compute='vehicle_detail')
    year = fields.Char(string="Year", compute='vehicle_detail')
    model = fields.Char(string="Model", compute='vehicle_detail')
    last_service_date = fields.Date(
        string="Last Service Date", compute="_last_service")
    vehicle_number_plate = fields.Char(string="Vehicle Number Plate")

    @api.multi
    def _last_service(self):
        for major_unit in self:
            bike = self.env['service.repair_order'].search(
                [('major_unit_id', '=', major_unit.id)], order='create_date desc', limit=1)
            major_unit.last_service_date = bike.done_date

    @api.model
    def default_get(self, fields):
        """ 
        In this function customer_id is directly taken from customer 
        and added by default in form view
        """
        res = super(CustomerRides, self).default_get(fields)
        if not res.get('partner_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'res.partner':
            res['partner_id'] = self.env.context['active_id']
        if self.env.context.get('partner_id'):
            res['partner_id'] = self.env.context['partner_id']
        return res

    @api.multi
    def vehicle_detail(self):
        major_unit_id = self.major_unit_ids.search([('id','=',self.id)])
        val = major_unit_id.prod_lot_id.product_id.attribute_value_ids
        self.make = val.filtered(lambda r: r.attribute_id == r.env.ref(
            'drm_product_attributes.product_attribute_make')).name
        self.model = val.filtered(lambda r: r.attribute_id == r.env.ref(
            'drm_product_attributes.product_attribute_model')).name
        self.year = val.filtered(lambda r: r.attribute_id == r.env.ref(
            'drm_product_attributes.product_attribute_year')).name
