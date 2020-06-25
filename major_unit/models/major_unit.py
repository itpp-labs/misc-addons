from odoo import api, fields, models, _
from odoo.exceptions import UserError

import odoo.addons.decimal_precision as dp


class MajorUnit(models.Model):
    _inherit = 'mail.thread'
    _inherits = {'stock.production.lot': 'prod_lot_id'}
    _name = 'major_unit.major_unit'
    _description = 'Major Unit'

    name = fields.Char(compute="_compute_major_unit_name", store=True)
    prod_lot_id = fields.Many2one(
        'stock.production.lot', string='Serial Number', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Vehicle', related='prod_lot_id.product_id', readonly=True)
    product_name = fields.Char(related='prod_lot_id.product_id.name', readonly=True)
    attribute_value_ids = fields.Many2many(
        'product.attribute.value', string='Attributes', related='prod_lot_id.product_id.attribute_value_ids',
        readonly=True)
    color_attr_id = fields.Many2one('product.attribute.value', string='Color', compute='_compute_color_attr_id')
    vin = fields.Char(related='prod_lot_id.name', store=True)
    vin_sn = fields.Char(
        compute='_compute_vin_sn', string='VIN',
        help='A unique number written on a vehicle motor (VIN/SN number)', copy=False, readonly=True)
    is_punched = fields.Boolean(string='Punched')
    finance_ids = fields.One2many('major_unit.finance', 'major_unit_id', string='Finance and Insurance')
    product_line_ids = fields.One2many('report.major_unit.product_line', 'major_unit_id', readonly=True)
    location_id = fields.Many2one('stock.location', 'Major Unit Location')
    #pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order.")
    #currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True, required=True)

    # total_price = fields.Float('Total Price', digits=dp.get_precision('Product Price'), compute='_compute_total_price')

    amount_untaxed = fields.Float(string='Untaxed Amount', readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Float(string='Taxes', readonly=True, compute='_amount_all', track_visibility='always')
    amount_total = fields.Float(string='Total', readonly=True, compute='_amount_all', track_visibility='always')
    form = fields.Selection(
        [('new', 'New'), ('used', 'Used'), ('consigned', 'Consigned'),('customer_owned','Customer Owned')], 'Form', default='new', required=True)
    sales_count = fields.Integer(compute='_compute_sales_count', string='# Sales', store=True)
    state = fields.Selection([
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('customer', 'At Customer')
    ], 'State', compute='_compute_state', store=True)
    stock_number = fields.Char(compute='_compute_stock_number', store=True)
    image = fields.Binary('Image', related='prod_lot_id.product_id.image_medium')
    major_unit_image_ids = fields.One2many('major_unit.image', 'major_unit_id', string='Images')
    miles = fields.Float(string='Miles', help='Number of miles last logged')
    miles_date = fields.Date(string="Miles Date", help='Date the miles were last logged')
    mileage = fields.Float(string='Mileage', help='Vehicle mileage')
    repair_order_ids = fields.One2many('service.repair_order', 'major_unit_id', 'Repair Orders')
    consignment_lowest_price = fields.Float('Lowest Price', digits=dp.get_precision('Product Price'))
    consignment_agreed_margin = fields.Float('Agreed Margin', help='Agreed Upon Commission Margin')
    standard_price = fields.Float(
        'Cost', digits=dp.get_precision('Product Price'), compute='_compute_standard_price',
        inverse='_set_standard_price')
    trade_in_price = fields.Float('Trade In Price')
    payoffs = fields.Float(
        'Outstanding Payoffs', digits=dp.get_precision('Product Price'), help='Outstanding loan payoffs')
    payoffs_description = fields.Text('Payoffs Description', help='Description of outstanding loan payoffs')
    trade_equity = fields.Float(
        'Trade Equity', digits=dp.get_precision('Product Price'), compute='_compute_trade_equity')

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")
    date_received = fields.Date(string="Date Received", help='Date the vehicle was received')
    manufacturer_holdback = fields.Float(string='Holdback ($)')
    manufacturer_percent_cost = fields.Float(string='Holdback (% Cost)')
    manufacturer_holdback_msrp = fields.Float(string='Holdback (% MSRP)')
    manufacturer_incentive = fields.Float(string='Incentive ($)')
    sale_price = list_price = fields.Float(related="product_id.product_tmpl_id.list_price")
    floored_by_bank = fields.Many2one('res.partner', string="Floored by", help='Bank with Flooring Loan', domain="[('is_company', '=', True)]")
    floored_amount = fields.Float(string='Amount Floored')
    free_flooring_date = fields.Date(string='Free Flooring Until')
    monthly_interest = fields.Float(string='Monthly Interest')
    date_sold = fields.Date(string='Date Sold', compute="_compute_so_info")
    date_registered = fields.Date(string='Date Registered')
    date_funded = fields.Date(string='Date Funded', compute="_compute_so_info")
    date_pdid = fields.Date(string='Date PDId')
    warranty_term = fields.Integer(string='Warranty Term', help='Major Unit Warranty Period')
    unit_class = fields.Selection([
        ('m', 'M'),
        ('s', 'S'),
    ], 'Class', help='Major Unit Class')
    purchased_from = fields.Char("Purchased From")
    nada_average_retail = fields.Float('NADA Average Retail',
                                       help="""Average Retail Value - (High Book)
                                       This figure reflects the average retail value of a used unit 'ready for resale'.
                                       Units in excellent or prime condition may increase value 10% - 15%.""",
                                       digits=dp.get_precision('Product Price'),
                                       compute='_compute_nada_average_retail',
                                       inverse='_set_nada_average_retail',
                                       )
    nada_rough_trade = fields.Float('NADA Rough Trade',
                                    help="""Rough Trade-In/Wholesale Value -
                                    This figure reflects the wholesale value of a used unit in need of repairs and refurbishing.""",
                                    digits=dp.get_precision('Product Price'),
                                    compute='_compute_nada_rough_trade',
                                    inverse='_set_nada_rough_trade',
                                    )

    def _search_related_nadanew_product_product(self):
        if 'nadanew.vehicle.product' in self.env:
            return self.env['nadanew.vehicle.product'].search([('odoo_id', '=', self.product_id.id)])

    @api.multi
    @api.depends('product_id')
    def _compute_nada_average_retail(self):
        for record in self:
            nada_product = record._search_related_nadanew_product_product()
            nada_average_retail = nada_product and nada_product.average_retail
            record.nada_average_retail = nada_average_retail or False

    @api.multi
    def _set_nada_average_retail(self):
        for record in self:
            nada_product = record._search_related_nadanew_product_product()
            if nada_product:
                nada_product.average_retail = record.nada_average_retail
            else:
                raise UserError(_("Related nadanew.vehicle.product record is not found."))

    @api.multi
    @api.depends('product_id')
    def _compute_nada_rough_trade(self):
        for record in self:
            nada_product = record._search_related_nadanew_product_product()
            nada_rough_trade = nada_product and nada_product.rough_trade
            record.nada_rough_trade = nada_rough_trade or False

    @api.multi
    def _set_nada_rough_trade(self):
        for record in self:
            nada_product = record._search_related_nadanew_product_product()
            if nada_product:
                nada_product.rough_trade = record.nada_rough_trade
            else:
                raise UserError(_("Related \"nadanew.vehicle.product\" record is not found."))

    # TODO: fields below are taken from @techspawn PR 86 and they will be computed from RO and Deal records in future.
    # last_service = fields.Date("Last Serviced Date", compute='...')
    # purchase_date = fields.Date(string='Purchase Date', help = 'Vehicle purchase date')
    # interest_paid_to_date = fields.Date(
    #     string='Interest Paid to Date',
    #     help='How much interest has been paid to date on the bike with the floor plan lender')
    # floor_plan_balance = fields.Date(string='Floor Plan Balance', help='How much debt is on the unit')
    # repair_order = fields.Char(
    #     string='Repair Order', help='Link to the Repair Order that relates to this particular Unit.')
    # partner_id = fields.Many2one(comodel_name='res.partner', string='Customer', readonly=False, required=True)

    # @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.product_line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            # currency = TODO
            order.update({
                # 'amount_untaxed': currency.round(amount_untaxed),
                # 'amount_tax': currency.round(amount_tax),
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.multi
    @api.depends('prod_lot_id', 'prod_lot_id.name')
    def _compute_major_unit_name(self):
        for record in self:
            if any(record.get_year_make_model_vin()):
                record.name = ("%s %s %s: %s" % (record.get_year_make_model_vin())).strip()

    @api.multi
    @api.depends('prod_lot_id', 'prod_lot_id.name', 'prod_lot_id.product_id',
                 'prod_lot_id.product_id.attribute_value_ids', 'form')
    def _compute_stock_number(self):
        for record in self:
            make = record.prod_lot_id.product_id.attribute_value_ids.filtered(
                lambda r: r.attribute_id == r.env.ref('drm_product_attributes.product_attribute_make'))
            state_char = 'N' if record.form == 'new' else 'U'
            if make:
                record.stock_number = "%s%s%s" % (state_char, make.name[0].upper(), record.prod_lot_id.name[-4:])
            elif record.prod_lot_id.name:
                record.stock_number = "%s%s" % (state_char, record.prod_lot_id.name[-4:])
            else:
                record.stock_number = 'New'

    @api.multi
    @api.depends('part_ids', 'part_ids.lst_price', 'service_ids', 'service_ids.lst_price', 'finance_ids',
                 'finance_ids.lst_price')
    def _compute_total_price(self):
        for record in self:
            part_total_price = sum([item.lst_price for item in record.part_ids])
            service_total_price = sum([item.lst_price for item in record.service_ids])
            finance_total_price = sum([item.lst_price for item in record.finance_ids])
            record.total_price = part_total_price + service_total_price + finance_total_price

    @api.multi
    @api.depends('prod_lot_id.product_id.attribute_value_ids')
    def _compute_color_attr_id(self):
        for record in self:
            record.color_attr_id = record.attribute_value_ids.filtered(
                lambda r: r.attribute_id == r.env.ref('drm_product_attributes.product_attribute_color'))

    @api.multi
    @api.depends('prod_lot_id', 'prod_lot_id.name')
    def _compute_vin_sn(self):
        for record in self:
            record.vin_sn = 'VIN: %s' % record.prod_lot_id.name

    @api.multi
    @api.depends('sale_order_line_ids', 'sale_order_line_ids.state')
    def _compute_sales_count(self):
        for record in self:
            record.sales_count = len(record.sale_order_line_ids.filtered(lambda r: r.state in ['sale', 'done']))

    @api.multi
    @api.depends('sales_count')
    def _compute_state(self):
        for record in self:
            if record.sales_count:
                record.state = 'sold'
            elif record.location_id.id == self.env.ref('stock.stock_location_customers').id:
                record.state = 'customer'
            elif record.sale_order_line_ids.filtered(lambda r: r.state == 'draft'):
                record.state = 'pending'
            else:
                record.state = 'available'

    @api.multi
    @api.depends('trade_in_price')
    def _compute_standard_price(self):
        for record in self:
            if record.trade_in_price:
                record.standard_price = record.trade_in_price
            else:
                record.standard_price = record.prod_lot_id.product_id.standard_price

    @api.multi
    @api.depends('standard_price', 'payoffs')
    def _compute_trade_equity(self):
        for record in self:
            record.trade_equity = record.standard_price - record.payoffs

    @api.multi
    @api.depends('state', 'sale_order_line_ids')
    def _compute_so_info(self):
        for record in self:
            if record.state is not 'available' and len(record.sale_order_line_ids):
                order = record.sale_order_line_ids[0].order_id
                record.date_sold = order.confirmation_date
                if order.invoice_status == 'invoiced':
                    payments_ids = map(lambda d: d.payment_ids, order.invoice_ids)
                    payments = []
                    for p in payments_ids:
                        payments += p
                    record.date_funded = max(map(lambda d: d.payment_date, payments))


    @api.multi
    def _set_standard_price(self):
        for record in self:
            record.trade_in_price = record.standard_price

    def get_major_unit_location(self):
        location = self.location_id
        if not location:
            location = self.env['stock.location'].create({
                'name': self.prod_lot_id.name})
            location.location_id=self.env.ref('major_unit.stock_location_major_units')
            self.location_id = location.id
        return location

    @api.multi
    def action_open_major_unit_parts(self):
        action = self.env.ref('major_unit.open_major_unit_parts_moves').read()[0]
        action['domain'] = [
            '|', ('location_id', '=', self.location_id.id), ('location_dest_id', '=', self.location_id.id)]
        return action

    @api.multi
    def action_view_sales(self):
        self.ensure_one()
        action = self.env.ref('major_unit.action_product_sale_list')

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            'domain': [('state', 'in', ['sale', 'done']),
                       ('product_id', '=', self.product_id.id),
                       ('lot_id', '=', self.prod_lot_id.id)],
        }

    def _create_major_unit(self, category_id, make_id, model_id, year_id, vin):
        """
        Find existing major unit by vin. If the record is not found, create it.
        :param int category_id: one of value of "category" product attribute: motorcycle, snowmobile, etc
        :param int make_id: id of 'product.attribute.value' record
        :param int model_id: id of 'product.attribute.value' record
        :param int year_id: id of 'product.attribute.value' record
        :param str vin:
        :return: major_unit.major_unit object
        """
        major_unit = self.search([('vin', '=', vin)])
        if not major_unit:
            product_product_obj = self.env['product.product']
            stock_production_lot_obj = self.env['stock.production.lot']
            product = product_product_obj.search([
                ('attribute_value_ids', '=', category_id),
                ('attribute_value_ids', '=', make_id),
                ('attribute_value_ids', '=', model_id),
                ('attribute_value_ids', '=', year_id),
            ], limit=1)
            if not product:
                attribute_value_obj = self.env['product.attribute.value']
                product = product_product_obj.create({
                    'name': ' '.join([attribute_value_obj.browse(item).name or '' for item in [year_id, make_id, model_id]]),
                    'categ_id': self.env.ref('major_unit.quartet_product_category_major_units').id,
                    'type': 'product',
                    'uom_id': self.env.ref('product.product_uom_unit').id,
                    'uom_po_id': self.env.ref('product.product_uom_unit').id,
                    'tracking': 'serial',
                    'details_model': 'nadanew.vehicle.product',
                    'attribute_value_ids': [(6, 0, [category_id, make_id, model_id, year_id])]
                })
            prod_lot = stock_production_lot_obj.create({
                'name': vin,
                'product_id': product.id,
            })
            major_unit = self.create({
                'prod_lot_id': prod_lot.id,
                'location_id': self.env.ref('stock.stock_location_customers').id,
            })
        return major_unit

    @api.multi
    def major_unit_to_quotation(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {
                'default_order_line': [(0,0, {
                    'name': self.name,
                    'price_unit': self.sale_price,
                    'product_id': self.product_id.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product_id.product_tmpl_id.uom_id.id,
                    'purchase_price': self.standard_price,
                    'lot_id': self.prod_lot_id.id,
                })],
                'default_details_model': 'sale.deal',
            }
        }

    def get_year_make_model_vin(self):
        attribute_value_ids = self.mapped('attribute_value_ids')
        year = attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_year)).name or ''
        make = attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_make)).name or ''
        model = attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_model)).name or ''
        if not any([year, make, model]):
            # we change model to let the strip method cut excessive white spaces
            model = self.prod_lot_id.product_id.name
        vin = self.prod_lot_id.name or ''
        return year, make, model, vin


class MajorUnitFinance(models.Model):
    _name = 'major_unit.finance'

    major_unit_id = fields.Many2one('major_unit.major_unit', 'Major Unit')
    product_id = fields.Many2one('product.product', 'Product')
    lst_price = fields.Float(
        'Sale Price', related='product_id.lst_price', digits=dp.get_precision('Product Price'), readonly=True,
        help="The sale price is managed from the product template. Click on the 'Variant Prices' button to set the"
             "extra attribute prices.")


class MajorUnitImage(models.Model):
    _name = 'major_unit.image'

    name = fields.Char('Name')
    image = fields.Binary('Image', attachment=True)
    major_unit_id = fields.Many2one('major_unit.major_unit', 'Related Major Unit', copy=True)
