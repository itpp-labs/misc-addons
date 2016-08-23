# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models

AVAILABLE_CONDITIONS = [
    ('0', 'Very Poor'),
    ('1', 'Poor'),
    ('2', 'Good'),
    ('3', 'Very Good'),
    ('4', 'Excellent'),
]

AVAILABLE_COURIERS = [
    ('0', 'Purolator'),
    ('1', 'Bus'),
    ('2', 'Other'),
]


class Loaner(models.Model):
    _name = 'mrp_loaner.loaner'
    _description = 'Loaner'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    type = fields.Selection(string="Type", selection=[('0', 'Autoclave'), ('1', 'Centrifuge'), ('2', 'Other'), ], required=True, )
    other_type = fields.Char(string="Other Type", required=False, )
    brand = fields.Char(string="Brand", required=True, )
    name = fields.Char(string="Model", required=True, )
    serial_number = fields.Char(string="Serial Number", required=True, )
    date_manufactured = fields.Date(string="Date Manufactured", required=False, default=fields.Date.today, )
    condition = fields.Selection(string="Condition", selection=AVAILABLE_CONDITIONS, required=False, track_visibility='onchange')
    notes = fields.Text(string="Notes", required=False, )
    active = fields.Boolean(default=True)
    usages = fields.One2many(comodel_name="mrp_loaner.loaner_usage", inverse_name="loaner_id", string="Usages", required=False, )
    accessories = fields.Char(string="Other Accessories", required=False, )

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for r in self.browse(cr, uid, ids, context=context):
            b = r.brand or ''
            n = r.name or ''
            s = ''
            if r.serial_number:
                s = 's/n ' + r.serial_number
            res.append((r.id, '%s %s %s' % (b, n, s)))
        return res


class LoanerUsage(models.Model):
    _name = 'mrp_loaner.loaner_usage'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Loaner Usage'

    loaner_id = fields.Many2one(comodel_name="mrp_loaner.loaner", string="Loaner Used", required=False, )

    accessory_cord = fields.Boolean(string="Cord", )
    accessory_rack = fields.Boolean(string="Rack", )
    accessory_trays = fields.Selection(string="Trays", selection=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ], required=False, )
    accessory_other = fields.Char(string="Other Accessories", required=False, )
    date_out = fields.Date(string="Date Loaner Sent", required=False, default=fields.Date.today)
    shipping_out_paid = fields.Boolean(string="Shipping Out Paid by us",)
    courier_out = fields.Selection(string="Outbound Courier", selection=AVAILABLE_COURIERS, required=False, )
    courier_out_other = fields.Char(string="Other Outbound Courier", required=False, )
    tracking_out = fields.Char(string="Outbound Tracking # ", required=False, )
    shipping_out_amount = fields.Float(string="Outbound Shipping Cost", required=False, )
    condition_out = fields.Selection(string="Condition When Sent", selection=AVAILABLE_CONDITIONS, required=False, )
    date_back = fields.Date(string="Date Loaner Returned", required=False)
    shipping_back_paid = fields.Boolean(string="Shipping Back Paid by us",)
    courier_back = fields.Selection(string="Return Courier", selection=AVAILABLE_COURIERS, required=False, )
    courier_back_other = fields.Char(string="Other Return Courier", required=False, )
    tracking_back = fields.Char(string="Return Tracking # ", required=False, )
    shipping_back_amount = fields.Float(string="Return Shipping Cost", required=False, )
    condition_back = fields.Selection(string="Condition When Returned", selection=AVAILABLE_CONDITIONS, required=False, )
    state = fields.Selection(string="State", selection=[('loan', 'On Loan'), ('testing', 'QC Testing'), ('done', 'Done'), ], required=False, default='loan')
    notes = fields.Text(string="Notes", required=False, )
