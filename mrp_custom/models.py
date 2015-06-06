# -*- coding: utf-8 -*-

from openerp import models, fields, api


class mrp_custom_jobs(models.Model):
    _name = 'mrp_custom.jobs'

    job_number = fields.Integer(readonly=True, required=True)
    job_name = fields.Char(compute='_get_name')
    routing_ids = fields.One2many(
        'mrp_custom.routing', 'job_id', string="Routings")
    material_ids = fields.One2many(
        'mrp_custom.routing', 'job_id', string="Material")

    customer_po = fields.Char(string='Customer PO')
    order_date = fields.Date(string='Order Date')
    requested_date = fields.Date(string='Requested Date')
    shipped_date = fields.Date(string='Snipped Date')
    status = fields.Char(string='Status')
    ship_via = fields.Char(string='Ship Via')
    shipTo_street1 = fields.Char(string='Ship to')
    shipTo_street2 = fields.Char()
    shipTo_country = fields.Char(string='Country')

    promised_date = fields.Date(string='Promised Date')
    sales_rep = fields.Char(string='Sales rep')
    sales_code = fields.Char(string='Sales Code')
    terms = fields.Char(string='Terms')
    invoice_date = fields.Date(string='Invoice Date')

    part_number = fields.Char(string='Part number')
    description = fields.Char(string='Part description')
    shipped_quantity = fields.Integer(string='Quantity snipped')
    order_quantity = fields.Integer(string='Quantity')
    unit_price = fields.Integer(string='Unit price')
    total_price = fields.Integer(string='Total price')
    ext_description = fields.Char(string='Part Ext Description')

    comment = fields.Text()

    @api.model
    def create(self, vals):
        job_env = self.env['mrp_custom.jobs']
        records = job_env.search([])
        if records:
            number = records[len(records) - 1].job_number + 1
        else:
            number = 1
        return super(mrp_custom_jobs, self).create({'job_number': number})
    
    @api.one 
    def _get_name(self):
        self.job_name = "Job " + str(self.job_number)


class mrp_custom_routing(models.Model):
    _name = 'mrp_custom.routing'
    job_id = fields.Many2one(
        'mrp_custom.jobs', ondelete='cascade', string="Job", required=True)
    work_center = fields.Char(string='Work Center')
    status = fields.Char(string='Status')
    run_pct_complete = fields.Integer(string='Run Pct Complete')
    est_run_hrs = fields.Integer(string='Est Hours')
    act_run_hrs = fields.Float(string='Actual Hours')


class mrp_custom_materials(models.Model):
    _name = 'mrp_custom.materials'
    job_id = fields.Many2one(
        'mrp_custom.jobs', ondelete='cascade', string="Job", required=True)
    material = fields.Char(string='Material')
    description = fields.Char(string='Description')
    vendor_ref = fields.Char(string='Vendor Ref')
    vendor = fields.Char(string='Vendor Name')
    unit_cost = fields.Float(string='Unit Cost')
    required_quantity = fields.Integer(string='Req Quantity')
    act_total_cost = fields.Char(string='Total_Cost')
