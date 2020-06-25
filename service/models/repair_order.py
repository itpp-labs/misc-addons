from odoo import fields, models, api

import odoo.addons.decimal_precision as dp

class CustomResPartner(models.Model):
    _inherit = 'res.partner'


class RepairOrder(models.Model):
    _inherit = 'service.repair_order'
    _description = 'Repair Order Module'

    standard_job_ids = fields.Many2many(comodel_name='service.standard_job',
                                        string='Standard Jobs',
                                        readonly=True)

    suggested_job_ids = fields.One2many('service.suggested.standard_job',
                                        'repair_order_id',
                                        string='Suggested Jobs',
                                        readonly=True)

class RepairOrderJobPart(models.Model):
    _inherit = 'service.repair_order.product'
    _description = 'Parts/Labor for Standard Job'
    
    state = fields.Selection([('draft', 'Draft'),
                          ('confirm', 'Confirm'),
                          ('cancel', 'Cancel'),
                          ],
                         copy=False,
                         track_visibility='onchange',
                         string='State',
                         required=True,
                         select=True,
                         default="draft")
    product_id = fields.Many2one(
        'product.product', 'Parts/Labor', required=True, domain=[('details_model', 'in', ['product.template.details', 'labor'])])

    # labor_charge = fields.Float(string="Labor Charge")


    # @api.multi
    # @api.depends('quantity', 'product_id', 'product_id.list_price')
    # def _compute_price(self):
    #     for product in self:
    #         product.price = (product.product_id.lst_price *
    #                          product.quantity) + product.labor_charge


    @api.multi
    @api.onchange('product_id')
    def _onchange_product_ids(self):
        for repair_order_obj in self:
          repair_order_obj.standard_job_id = repair_order_obj.repair_order_id.standard_job_ids

class StandardJobPart(models.Model):
    _name = 'service.suggested.standard_job'
    _description = 'Suggested Standard Job'

    repair_order_id = fields.Many2one('service.repair_order',
                                      'Repair Order',
                                      required=True,
                                      ondelete='cascade',
                                      states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]})

    product_id = fields.Many2one('product.product',
                                 'Parts/Labor',
                                 required=True,
                                 domain=[
                                     ('details_model', 'in', ['product.template.details', 'labor'])],
                                 states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]})

    standard_job_id = fields.Many2one('service.standard_job', 'Standard Job')

    inspection_id = fields.Many2one('service.inspection', 'Inspection',
                                    states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]})

    quantity = fields.Float('Quantity',
                            digits=dp.get_precision('Product Unit of Measure'),
                            default=1,
                            states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]})

    qty_available = fields.Float('Inventory',
                                 digits=dp.get_precision(
                                     'Product Unit of Measure'),
                                 related='product_id.qty_available',
                                 states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]})
    sequence = fields.Integer('Sequence')
    unit_price = fields.Float('Unit Price',
                              digits=dp.get_precision('Product Price'),
                              related='product_id.lst_price',
                              states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]})
    taxes_id = fields.Many2many('account.tax',
                                related='product_id.taxes_id',
                                readonly=True,
                                states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]})
    price = fields.Float('Subtotal',
                         compute='_compute_price',
                         digits=dp.get_precision('Product Price'),
                         states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]})

    state = fields.Selection([('suggested', 'Suggested'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected'),
                              ],
                             copy=False,
                             track_visibility='onchange',
                             string='State',
                             required=True,
                             select=True,
                             default="suggested",
                             states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]})

    @api.model
    def default_get(self, fields):
        res = super(StandardJobPart, self).default_get(fields)
        if not res.get('repair_order_id') and self.env.context.get('active_model') == 'service.repair_order':
            res['repair_order_id'] = self.env['service.repair_order'].browse(
                self.env.context['active_id']).id
        return res

    @api.multi
    @api.depends('quantity', 'product_id', 'product_id.list_price')
    def _compute_price(self):
        for product in self:
            product.price = product.product_id.lst_price * product.quantity


    # product_repair_ids = fields.One2many('service.repair_order',
    #                                          'repair_order_id',
    #                                          required=False,
    #                                          )

    # repair_order_count = fields.Integer('# Repair Order',
    #                                           compute='_compute_repair_order_count',)
    
    # @api.one
    # @api.depends('product_repair_ids')
    # def _compute_repair_order_count(self):
    #   self.repair_order_count = len(self.product_repair_ids)



class ServiceApplyStandardJobsCustom(models.TransientModel):
    _inherit = "service.apply.standard.job"

    @api.onchange('repair_order_id')
    def _onchange_repair_order(self):
        major_unit = self.env['major_unit.major_unit'].browse(self.env.context.get('major_unit_id'))
        fitments = self.env['product.fitment'].get_fitment_by_make_model_year(self.get_make_model_year(major_unit))
        return {'domain': {'standard_job_ids': [('recall', '=', False)]}}

    @api.multi
    def apply_standard_job(self):
        obj=self.env['service.repair_order'].search([('id','=',self.repair_order_id.id)])
        obj.write({'standard_job_ids':[(4, x) for x in self.standard_job_ids.ids]})
        for wizard in self:
            for standard_job in wizard.standard_job_ids:
                for product_line in standard_job.product_ids:
                    self.env['service.repair_order.product'].create({
                        'repair_order_id': wizard.repair_order_id.id,
                        'product_id': product_line.product_id.id,
                        'standard_job_id': standard_job.id,
                        'quantity': product_line.quantity,
                    })