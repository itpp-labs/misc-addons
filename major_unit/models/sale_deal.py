from odoo import api, fields, models


class SaleDeal(models.Model):
    _inherit = 'mail.thread'
    _name = 'sale.deal'
    _description = "Deal"

    name = fields.Char(string='Name', required=True, copy=False, index=True, default='New')
    attachment_ids = fields.One2many('sale.deal.attachment', 'deal_id', string='Attachments')
    trade_in_mu_ids = fields.Many2many('major_unit.major_unit', string='Major Units')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')

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

    @api.multi
    @api.depends('sale_order_id', 'payment_previous', 'payment_down', 'trade_equity')
    def _compute_totals(self):
        for record in self:
            record.total_cash_price = record.sale_order_id.amount_total
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
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.deal') or 'New'
        result = super(SaleDeal, self).create(vals)
        sale_deal_attachment_obj = self.env['sale.deal.attachment']
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
                     'Proof of Insurance']:
            sale_deal_attachment_obj.create({
                'deal_id': result.id,
                'name': form,
            })
        return result


class SaleDealAttachment(models.Model):
    _name = 'sale.deal.attachment'
    _description = "Deal Attachments"

    name = fields.Char(string='Name', required=True)
    deal_id = fields.Many2one('sale.deal', string='Major Units')
    file_ids = fields.One2many('sale.deal.attachment.file', 'attachment_id', string='Attachments')


class SaleDealAttachmentFile(models.Model):
    _name = 'sale.deal.attachment.file'
    _inherit = 'web.preview'
    _preview_media_file = 'file'

    name = fields.Char(string='Name', required=True)
    file = fields.Binary('File', attachment=True)
    attachment_id = fields.Many2one('sale.deal.attachment')
