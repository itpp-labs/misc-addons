import logging
from odoo import models, fields, api, _
from odoo import tools


class ServiceReport(models.Model):
    _name = "custom.service.report"
    _description = "Service Statistics"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Customer ID', readonly=True)
    amt_untaxed = fields.Float(string="Untaxed Amount", readonly=True)
    date = fields.Datetime('Date Order', readonly=True)
    amt_total = fields.Float(string="Amount total", readonly=True)
    amt_tax = fields.Float(string="Tax Amount", readonly=True)
    date_start = fields.Datetime('Start Date', readonly=True)
    end_date = fields.Datetime("End Date", readonly=True)
    requested_date = fields.Date(
        "Scheduled Date", readonly=True, default=fields.Datetime.now)
    nbr = fields.Integer('# of Tasks', readonly=True)
    major_unit_id = fields.Many2one(comodel_name='major_unit.major_unit',
                                    string='Vehicle',
                                    domain="[('partner_id', '=', partner_id)]",
                                    readonly=True,

                                    )
    repair_type = fields.Selection([('repair_order', 'Repair Order'),
                                    ('pdi', 'PDI'),
                                    ('comeback', 'Comeback')
                                    ],
                                   String='Priority',
                                   readonly=True,
                                   )
    # model = fields.Char(string="Model", readonly=True)
    # make = fields.Char(string="Make", readonly=True)
    # year = fields.Char(string="Year", readonly=True)
    # vin = fields.Char(string="VIN", readonly=True)
    miles = fields.Char(string="Miles", readonly=True)

    # licence_no = fields.Char(string="Licence No", readonly=True)
    mileage = fields.Char(string="Mileage", readonly=True)
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template', readonly=True)
    # color = fields.Char(string="Color", readonly=True)
    state = fields.Selection([('QUOTE', 'Quote'),
                              ('APPROVE', 'Approve'),
                              ('PARTS', 'Parts'),
                              ('PICKUP', 'Pickup'),
                              ('INSPECT', 'Inspect'),
                              ('LIFT', 'Lift'),
                              ('TEST', 'Test'),
                              ('COMPLETE', 'Complete'),
                              ('DELIVER', 'Deliver'),
                              ('CANCEL', 'Cancel'),
                              ],
                             string='State',
                             readonly=True,
                             )
    name = fields.Char(string="Order Number")
    pickup = fields.Boolean(string="Pickup Required", readonly=True)
    warranty = fields.Boolean(string="Warranty",
                              help="Service vehicle warranty",
                              readonly=True)
    # pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=False, readonly=True, states={
    #                                'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order.")
    # vehicle_service_type = fields.Many2one(comodel_name='service.repair_order.type',
    #                                        string='Vehicle Service Type',
    #                                        readonly=True,

    #                                        )
    parts = fields.Many2one(comodel_name='product.product',
                            string='Product',
                            readonly=True,
                            )
    miles_date = fields.Date(string='Miles Date',
                             help='Vehicle Miles date', readonly=True)
    price = fields.Float(string="Subtotal",readonly=True)
    loaner = fields.Boolean(string="Loaner Bikes Required",readonly=True)
    urgency = fields.Selection([('0', 'Low'),
                                ('1', 'Medium'),
                                ('2', 'High'),
                                ('3', 'Highest')],
                               String='Priority',readonly=True)
    pickup_time = fields.Datetime(string="Pickup Time",readonly=True)
    mechanic_id = fields.Many2one(comodel_name='hr.employee',
                                  string='Mechanic',readonly=True)

    def _select(self):
        select_str = """
        WITH currency_rate as (%s)
             SELECT 
                    sum(t.amount_total / COALESCE(cr.rate, 1.0)) as amt_total,
                    t.amount_tax as amt_tax,
                    t.amount_untaxed as amt_untaxed,                    
                    min(l.id) as id,
                    l.product_id as parts,
                    (select 1 ) AS nbr,                    
                    t.partner_id as partner_id,
                    t.major_unit_id as major_unit_id,                    
                    t.start_date as date_start,
                    t.start_date as date,
                    t.end_date as end_date,
                    t.requested_date as requested_date,                    
                    v.miles as miles,
                    v.miles_date as miles_date,
                    v.mileage as mileage,
                    t.repair_type as repair_type,
                    t.loaner as loaner,
                    t.urgency as urgency,
                    t.pickup_time as pickup_time,
                    t.warranty as warranty,
                    t.mechanic_id as mechanic_id,
                    -- v.licence_no as licence_no,
                    -- v.purchase_date as purchase_date,
                    t.state as state,
                    t.name as name,
                    t.pickup as pickup,                    
                    p.product_tmpl_id,
                    sum(l.price / COALESCE(cr.rate, 1.0)) as price,
                    extract(epoch from avg(date_trunc('day',t.start_date)-date_trunc('day',t.create_date)))/(24*60*60)::decimal(16,2) as delay
                    

        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _from(self):
        from_str = """
                major_unit_major_unit v
                  join service_repair_order t on (t.major_unit_id=v.id)             
                   join service_repair_order_product l on (l.repair_order_id=t.id)
                        left join product_product p on (l.product_id=p.id)
                        left join product_template pt on (p.product_tmpl_id=pt.id)
                        
                left join product_uom u2 on (u2.id=pt.uom_id)
                    left join product_pricelist pp on (t.pricelist_id = pp.id)
                    left join currency_rate cr on (cr.currency_id = pp.currency_id and
                        cr.company_id = t.company_id and
                        cr.date_start <= coalesce(t.start_date, now()) and
                        (cr.date_end is null or cr.date_end > coalesce(t.start_date, now())))
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    l.product_id,
                    t.id,
                    t.partner_id,
                    t.amount_tax,
                    t.amount_untaxed,                                        
                    l.repair_order_id,                    
                    t.major_unit_id,
                    v.mileage,                    
                    v.miles,
                    v.miles_date,
                    t.repair_type,
                    t.pickup,
                    t.mechanic_id,
                    t.urgency,
                    p.product_tmpl_id
                    
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""CREATE or REPLACE VIEW %s as 
            %s
            FROM  %s                 
            %s
        """ % (self._table, self._select(), self._from(), self._group_by()))
