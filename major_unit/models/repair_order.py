from odoo import fields, models, api

import odoo.addons.decimal_precision as dp


class RepairOrder(models.Model):
    _inherit = 'mail.thread'
    _name = 'service.repair_order'
    _description = 'Repair Order'

    @api.model
    def _default_stock_location(self):
        """ Changed current part location to default location according to the warehouse of company """
        company = self.env['res.company']._company_default_get('service')
        # warehouse = self.env.ref('stock.warehouse0', raise_if_not_found=False)
        # if warehouse:
            # return warehouse.lot_stock_id.id
        if company:
            ware = self.env['stock.warehouse'].search([('company_id','=',company.id)])
            return ware.lot_stock_id.id
        return False

    name = fields.Char(
        string='Order Reference', required=True, copy=False, readonly=True, index=True, default='New')
    major_unit_id = fields.Many2one(
        'major_unit.major_unit', string='Vehicle', required=True, ondelete='cascade')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True)
    product_ids = fields.One2many(
        'service.repair_order.product', 'repair_order_id', string='Parts/Labor', required=True)
    part_location_id = fields.Many2one(
        'stock.location', 'Current Part Location', default=_default_stock_location, readonly=True,
        required=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status', readonly=True, copy=False, track_visibility='onchange', default='draft')

    amount_untaxed = fields.Float(
        string='Untaxed Amount', store=True, readonly=True, compute='_compute_amount_all',
        digits=dp.get_precision('Product Price'))
    amount_tax = fields.Float(
        string='Taxes', store=True, readonly=True, compute='_compute_amount_all',
        digits=dp.get_precision('Product Price'))
    amount_total = fields.Float(
        string='Total', store=True, readonly=True, compute='_compute_amount_all',
        digits=dp.get_precision('Product Price'))

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'major_unit.repair_order') or 'New'
        result = super(RepairOrder, self).create(vals)
        return result

    @api.depends('product_ids.price')
    def _compute_amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.product_ids:
                amount_untaxed += line.price
                amount_tax += line.price * \
                    sum(line.taxes_id.mapped('amount')) / 100
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.multi
    def action_confirm(self):
        major_unit_location = self.major_unit_id.get_major_unit_location()
        for product_line in self.product_ids:
            if product_line.product_id.details_model != 'product.template.details':
                continue
            part_move = self.env['stock.move'].create({
                'name': 'Repair order #%s' % self.name,
                'product_id': product_line.product_id.id,
                'product_uom': product_line.product_id.uom_id.id,
                'product_uom_qty': product_line.quantity,
                'state': 'confirmed',
                'location_id': self.part_location_id.id,
                'location_dest_id': major_unit_location.id,
            })
            part_move._action_confirm()
        # self.write({'state': 'done'})

    @api.multi
    def action_undo(self):
        major_unit_location = self.major_unit_id.get_major_unit_location()
        for product_line in self.product_ids:
            if product_line.product_id.details_model != 'product.template.details':
                continue
            part_move = self.env['stock.move'].create({
                'name': 'Undo Repair order #%s' % self.name,
                'product_id': product_line.product_id.id,
                'product_uom': product_line.product_id.uom_id.id,
                'product_uom_qty': product_line.quantity,
                'state': 'confirmed',
                'location_id': major_unit_location.id,
                'location_dest_id': self.part_location_id.id,
            })
            part_move._action_confirm()
        self.write({'state': 'done'})


class RepairOrderJobPart(models.Model):
    _name = 'service.repair_order.product'
    _description = 'Parts/Labor for Standard Job'

    repair_order_id = fields.Many2one(
        'service.repair_order', 'Repair Order', required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', 'Parts/Labor', required=True, domain=[('details_model', 'in', ['product.template.details', 'labor'])])
    standard_job_id = fields.Many2one('service.standard_job', 'Standard Job')
    quantity = fields.Float('Quantity', digits=dp.get_precision(
        'Product Unit of Measure'), default=1)
    qty_available = fields.Float(
        'Inventory', digits=dp.get_precision('Product Unit of Measure'), related='product_id.qty_available')
    sequence = fields.Integer('Sequence')
    unit_price = fields.Float(
        'Unit Price', digits=dp.get_precision('Product Price'), related='product_id.lst_price')
    taxes_id = fields.Many2many(
        'account.tax', related='product_id.taxes_id', readonly=True)
    price = fields.Float('Subtotal', compute='_compute_price',
                         digits=dp.get_precision('Product Price'), store=True)

    @api.model
    def default_get(self, fields):
        res = super(RepairOrderJobPart, self).default_get(fields)
        if not res.get('repair_order_id') and self.env.context.get('active_model') == 'service.repair_order':
            res['repair_order_id'] = self.env['service.repair_order'].browse(
                self.env.context['active_id']).id
        return res

    @api.multi
    @api.depends('quantity', 'product_id', 'product_id.list_price')
    def _compute_price(self):
        for product in self:
            product.price = product.product_id.lst_price * product.quantity
