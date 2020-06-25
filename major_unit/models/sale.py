from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'base_details']

    profitability_line_ids = fields.One2many('sale.order.line', 'order_id', string='Profitability', readonly=True)
    # sale_deal_id = fields.One2many('sale.deal', 'sale_order_id', string='Deal')

    attachment_ids = fields.One2many('sale.order.attachment', 'order_id', string='Attachments')
    trade_in_mu_ids = fields.Many2many('major_unit.major_unit', string='Major Units')

    loan_term = fields.Integer(string='Loan Term')
    days_first = fields.Integer(string='Days to First')
    ballon_term = fields.Integer(string='Ballon Term')
    apr = fields.Float(string='APR (%)', digits=(16, 2))
    dealer_rate = fields.Float(string='Dealer (%)', digits=(16, 2))
    payment_previous = fields.Float(string='Previous Payments', digits=(16, 2))
    payment_down = fields.Float(string='Down Payments', digits=(16, 2))
    payment = fields.Float(compute='_compute_payment', string='Payment', digits=(16, 2))
    trade_equity = fields.Float(string='Trade Equity', digits=(16, 2), compute='_compute_trade_equity')
    total_cash_price = fields.Float(compute='_compute_totals', string='Total Cash Price', digits=(16, 2))
    total_down = fields.Float(string='Down', digits=(16, 2), compute='_compute_totals')
    total_to_finance = fields.Float(string='Total to Finance', digits=(16, 2), compute='_compute_totals')
    total_apr = fields.Float(string='Total APR', digits=(16, 2), compute='_compute_total_apr')

    vendor = fields.Many2one('res.partner', string='Vendor', domain="[('supplier', '=', True)]")
    dealer_number = fields.Char('Dealer Number')
    total_price = fields.Float('Total Price', digits=dp.get_precision('Product Price'), default='0')
    total_equity = fields.Float('Total Equity', digits=dp.get_precision('Product Price'), default='0')
    finance_charges = fields.Float('Finance Charges', digits=dp.get_precision('Product Price'), default='0')
    number_of_payments = fields.Integer('Number of Payments', default='0')
    payment_amount = fields.Integer('Payment Amount', default='0')
    might_need_more = fields.Integer('Might Need More', default='0')

    @api.multi
    @api.depends('payment_previous', 'payment_down', 'trade_equity')
    def _compute_totals(self):
        for record in self:
            record.total_cash_price = record.amount_total
            record.total_down = record.payment_previous + record.payment_down + record.trade_equity
            record.total_to_finance = record.total_cash_price - record.total_down

    @api.multi
    @api.depends('loan_term', 'total_to_finance', 'total_apr')
    def _compute_payment(self):
        for record in self:
            total_to_finance = record.total_to_finance
            total_apr = record.total_apr
            loan_term = float(record.loan_term)
            try:
                payment = total_to_finance * (total_apr / 1200) / (1 - 1 / (1 + (total_apr / 1200)) ** loan_term)
            except ZeroDivisionError:
                payment = False
            record.payment = payment or 0.00

    @api.multi
    @api.depends('apr', 'dealer_rate')
    def _compute_total_apr(self):
        for record in self:
            record.total_apr = record.apr + record.dealer_rate

    @api.multi
    @api.depends('apr', 'dealer_rate')
    def _compute_trade_equity(self):
        for record in self:
            record.trade_equity = sum(record.trade_in_mu_ids.mapped('trade_equity'))

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or 'New'
        result = super(SaleOrder, self).create(vals)
        sale_order_attachment_obj = self.env['sale.order.attachment']
        for form in ['Lemon Law',
                     'Bill of Sale',
                     'Warranty Disclaimer',
                     'Insurance Products',
                     'Promissory Note',
                     'Odometer Disclosure',
                     'Retail Installment Contract (Form 553-WA)',
                     'Release of Interest Power of Attorney',
                     'Title',
                     'Affidavit of Lost Title',
                     'Temporary Permit',
                     'Letter of Guarantee',
                     'Authorization to Payoff',
                     'Driver’s License',
                     'Proof of Income',
                     'Proof of Insurance',
                     ]:
            sale_order_attachment_obj.create({
                'order_id': result.id,
                'name': form,
            })
        return result

    def _model_selection(self):
        selection = super(SaleOrder, self)._model_selection()
        selection.append(('sale.deal', 'Major Unit Deal'))
        return selection

    # @api.multi
    # def write(self, vals):
    #     details_res_id = vals.get('details_res_id') or self.details_res_id
    #     details_model = vals.get('details_model') or self.details_model
    #     if details_model == 'sale.deal' and details_res_id:
    #         self.env['sale.deal'].search([('id', '=', details_res_id)]).write({
    #             'sale_order_id': self.id,
    #         })
    #     return super(SaleOrder, self).write(vals)


class SaleOrderAttachment(models.Model):
    _name = 'sale.order.attachment'
    _description = "Order Attachments"

    name = fields.Char(string='Name', required=True)
    order_id = fields.Many2one('sale.order', string='Major Units')
    file_ids = fields.One2many('sale.order.attachment.file', 'attachment_id', string='Attachments')


class SaleOrderAttachmentFile(models.Model):
    _name = 'sale.order.attachment.file'
    _inherit = 'web.preview'
    _preview_media_file = 'file'

    name = fields.Char(string='Name', required=True)
    file = fields.Binary('File', attachment=True)
    attachment_id = fields.Many2one('sale.order.attachment')


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_rate = fields.Float(
        compute='_compute_margin_values', string='Margin (%)',digits=dp.get_precision('Product Price'))
    backend = fields.Float('Backend', digits=dp.get_precision('Product Price'), default=0.0)
    margin_full = fields.Float(compute='_compute_margin_values', digits=dp.get_precision('Product Price'))
    margin_full_rate = fields.Float(
        compute='_compute_margin_values', string='Full (%)', digits=dp.get_precision('Product Price'))
    is_trade_in_payment = fields.Boolean('Trade-in Payment', default=False)

    @api.multi
    @api.depends('margin', 'price_unit', 'backend')
    def _compute_margin_values(self):
        for record in self:
            record.margin_rate = record.margin * 100 / record.price_unit if record.price_unit else 0
            record.margin_full = record.margin + record.backend
            record.margin_full_rate = record.margin_full * 100 / record.price_unit if record.price_unit else 0
