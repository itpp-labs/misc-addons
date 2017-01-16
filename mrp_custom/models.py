# -*- coding: utf-8 -*-

from openerp import models, fields, api


class MrpCustomJobs(models.Model):
    _name = 'mrp_custom.jobs'
    job_number = fields.Integer(string="Job Number")
    job_name = fields.Char(compute='_get_name')
    _rec_name = 'job_name'
    routing_ids = fields.One2many(
        'mrp_custom.routing', 'job_id', string="Routing")
    material_ids = fields.One2many(
        'mrp_custom.material', 'job_id', string="Material")
    cases_ids = fields.One2many(
        'mrp_custom.cases', 'job_id', string="Cases")
    contacts_id = fields.Many2one(
        'mrp_custom.contacts',
        ondelete='cascade',
        required=True,
        string="Contact",
        delegate=True)

    customer_po = fields.Char(string='Customer PO')
    order_date = fields.Char(string='Order Date')
    requested_date = fields.Char(string='Requested Date')
    shipped_date = fields.Char(string='Shipped Date')
    status = fields.Char(string='Status')
    ship_via = fields.Char(string='Ship Via')
    shipTo_street1 = fields.Char(string='Ship to street1')
    shipTo_street2 = fields.Char(string='Ship to street2')
    shipTo_country = fields.Char(string='Ship to Country')

    promised_date = fields.Char(string='Promised Date')
    sales_rep = fields.Char(string='Sales rep')
    sales_code = fields.Char(string='Sales Code')
    terms = fields.Char(string='Terms')
    invoice_date = fields.Char(string='Invoice Date')

    part_number = fields.Char(string='Part number')
    description = fields.Char(string='Description')
    shipped_quantity = fields.Integer(string='Shipped Quantity')
    order_quantity = fields.Integer(string='Order Quantity')
    unit_price = fields.Integer(string='Unit price')
    total_price = fields.Char(string='Total price')
    ext_description = fields.Char(string='Ext Description')

    comment = fields.Text(string='Comment')

    @api.multi
    def _get_name(self):
        for r in self:
            r._get_name_one()
        return True

    @api.multi
    def _get_name_one(self):
        self.ensure_one()
        self.job_name = "Job " + str(self.job_number)


class MrpCustomRouting(models.Model):
    _name = 'mrp_custom.routing'
    job_id = fields.Many2one(
        'mrp_custom.jobs', ondelete='cascade', string="Job", required=True)
    work_center = fields.Char(string='Work Center')
    status = fields.Char(string='Status')
    run_pct_complete = fields.Integer(string='Run pct complete')
    est_run_hrs = fields.Char(string='Est run hours')
    act_run_hrs = fields.Char(string='Actual run hours')


class MrpCustomMaterial(models.Model):
    _name = 'mrp_custom.material'
    job_id = fields.Many2one(
        'mrp_custom.jobs', ondelete='cascade', string="Job", required=True)
    material = fields.Char(string='Material')
    description = fields.Char(string='Description')
    vendor_ref = fields.Char(string='Vendor ref')
    vendor = fields.Char(string='Vendor')
    unit_cost = fields.Char(string='Unit cost')
    required_quantity = fields.Char(string='Req quantity')
    act_total_cost = fields.Char(string='Act total cost')


class MrpCustomCases(models.Model):
    _name = 'mrp_custom.cases'
    job_id = fields.Many2one(
        'mrp_custom.jobs', ondelete='cascade', string="Job", required=True)
    num = fields.Integer(string='Num.')
    subject = fields.Char(string='Subject')
    account_name = fields.Char(string='Account Name')
    status = fields.Char(string='Status')
    date_created = fields.Char(string='Date Created')
    assigned_user = fields.Char(string='Assigned User')


class MrpCustomContacts(models.Model):
    _name = 'mrp_custom.contacts'
    contact_name = fields.Char(string="Contact Name")
    _rec_name = 'contact_name'

    contact_street_address = fields.Char(string="Contact street address")
    contact_street_address_2 = fields.Char(string="Contact street address 2")
    contact_cell_phone = fields.Char(string="Contact cell phone")
    contact_city = fields.Char(string="Contact city")
    contact_country = fields.Char(string="Contact country")
    contact_fax = fields.Char(string="Contact fax")
    contact_phone = fields.Char(string="Contact phone")
    contact_state = fields.Char(string="Contact state")
    contact_zip = fields.Char(string="Contact zip")
    email_address = fields.Char(string="Email address")
    fax = fields.Char(string="Fax")
    note_text = fields.Char(string="Note text")
    phone = fields.Char(string="Phone")
    shipto_cell_phone = fields.Char(string="Ship to cell phone")
    shipto_city = fields.Char(string="Shipto city")
    shipto_company_name = fields.Char(string="Ship to company name")
    shipto_fax = fields.Char(string="Ship to fax")
    shipto_name = fields.Char(string="Ship to name")
    shipto_phone = fields.Char(string="Ship to phone")
    shipto_state = fields.Char(string="Ship to state")
    shipto_zip = fields.Char(string="Ship to zip")
    shiptto_customer = fields.Char(string="Ship to customer")
