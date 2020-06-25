from odoo import api, fields, models

import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"


    @api.onchange('details_model')
    def _set_labor_type(self):
        for r in self:
            if r.details_model == 'labor':
                r.type = 'service'


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange('details_model')
    def _set_labor_type(self):
        for r in self:
            if r.details_model == 'labor':
                r.type = 'service'


class StandardJob(models.Model):
    _inherit = 'mail.thread'
    _name = 'service.standard_job'
    _description = 'Standard Job'

    name = fields.Char(string='Description', required=True)
    # vehicle_ids = fields.Many2many(  # Temporary solution, it's should be replaced with fitment
    #     'product.product', 'service_standard_job_vehicle_product_product_rel', 'standard_job_id',
    #     'product_id', string='Units', domain=[('details_model', '=', 'vehicle')])
    product_ids = fields.One2many(
        'service.standard_job.product', 'standard_job_id', string='Products')
    fitment_ids = fields.Many2many('product.fitment', 'standard_job_fitment_rel', 'product_id', 'fitment_id', string='Fitment')
    # Recall job fields
    recall = fields.Boolean(string="Recall", default=False)
    manufacturer = fields.Char(string="Manufacturer")
    claim_id = fields.Char(string="Claim Id")
    defect_type = fields.Char(string="Defect Type")
    defect_group = fields.Char(string="Defect Group")
    defect_code = fields.Char(string="Defect Code")
    cause = fields.Text(string="Cause")
    instruction = fields.Binary(string='Instruction')
    recall_job_image_ids = fields.One2many('recall_job.image', 'recall_job_id', string="Photos")

    @api.model
    def default_get(self, fields):
        res = super(StandardJob, self).default_get(fields)
        if self.env.context.get('search_default_recall'):
            res['recall'] = True
        return res
    """
    year_ids = fields.Many2many(
        'product.attribute.value', 'service_standard_job_year_product_attribute_value_rel', 'standard_job_id',
        'product_attribute_value_id', string='Year',
        domain=lambda self: [('attribute_id', '=', self.env.ref('drm_product_attributes.product_attribute_year').id)])
    year_all = fields.Boolean('All Years', default=False)
    make_ids = fields.Many2many(
        'product.attribute.value', 'service_standard_job_make_product_attribute_value_rel', 'standard_job_id',
        'product_attribute_value_id', string='Make',
        domain=lambda self: [('attribute_id', '=', self.env.ref('drm_product_attributes.product_attribute_make').id)])
    make_all = fields.Boolean('All Makes', default=False)
    model_ids = fields.Many2many(
        'product.attribute.value', 'service_standard_job_model_product_attribute_value_rel', 'standard_job_id',
        'product_attribute_value_id', string='Model',
        domain=lambda self: [('attribute_id', '=', self.env.ref('drm_product_attributes.product_attribute_model').id)])
    model_all = fields.Boolean('All Models', default=False)

    @api.onchange('year_all')
    def onchange_year_all(self):
        if self.year_all:
            self.year_ids = None

    @api.onchange('make_all')
    def onchange_make_all(self):
        if self.make_all:
            self.make_ids = None

    @api.onchange('model_all')
    def onchange_model_all(self):
        if self.model_all:
            self.model_ids = None
    """


class StandardJobPart(models.Model):
    _name = 'service.standard_job.product'
    _description = 'Products for Standard Job'

    product_id = fields.Many2one(
        'product.product', 'Part/Labor', required=True, domain=[('details_model', 'in', ['product.template.details', 'labor'])])
    standard_job_id = fields.Many2one('service.standard_job', 'Standard Jobs')
    quantity = fields.Float('Quantity', digits=dp.get_precision('Product Unit of Measure'), default=1)
    sequence = fields.Integer('Sequence', default=1)
    categ_id = fields.Many2one('product.category', 'Internal Category', related='product_id.categ_id')
    attribute_value_ids = fields.Many2many(
        'product.attribute.value', 'Attributes', related='product_id.attribute_value_ids')
    unit_price = fields.Float(
        'Unit Price', digits=dp.get_precision('Product Price'), related='product_id.lst_price')
    price = fields.Float('Subtotal', compute='_compute_price', digits=dp.get_precision('Product Price'))

    @api.multi
    @api.depends('quantity', 'product_id', 'product_id.list_price')
    def _compute_price(self):
        for product in self:
            product.price = product.product_id.list_price * product.quantity


class RecallJobImage(models.Model):
    _name = 'recall_job.image'

    name = fields.Char(string='Name')
    image = fields.Binary(string='Image')
    recall_job_id = fields.Many2one('service.standard_job', 'Related Recall Job', copy=True)

"""
class StandardJobLabor(models.Model):
    _name = 'service.standard_job.labor'
    _description = 'Labors for Standard Job'

    labor_id = fields.Many2one(
        'product.product', 'Labor', required=True, domain=[('details_model', '=', 'labor')])
    standard_job_id = fields.Many2one('service.standard_job', 'Standard Jobs')
    quantity = fields.Integer('Quantity', default=1)
    sequence = fields.Integer('Sequence', related='labor_id.sequence')
    attribute_value_ids = fields.Many2many(
        'product.attribute.value', 'Attributes', related='labor_id.attribute_value_ids')
    list_price = fields.Float('Sale Price', compute='_compute_list_price', digits=dp.get_precision('Product Price'))

    @api.multi
    @api.depends('quantity', 'labor_id', 'labor_id.list_price')
    def _compute_list_price(self):
        for labor in self:
            labor.list_price = labor.labor_id.list_price * labor.quantity
"""
