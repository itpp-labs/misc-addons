from odoo import models, fields, api


class Fitment(models.Model):
    _name = 'product.fitment'
    _product_attribute_make = 'drm_product_attributes.product_attribute_make'
    _product_attribute_model = 'drm_product_attributes.product_attribute_model'
    _product_attribute_year = 'drm_product_attributes.product_attribute_year'

    name = fields.Char(
        string='Order Reference', required=True, copy=False, readonly=True, default='New')
    # type = fields.Selection([
    #     ('product', 'Parts and Accessories'),
    #     ('job', 'Standard Jobs'),
    # ], string='Fitment for', default='product', required=True)
    part_accessory_ids = fields.Many2many(
        'product.product', 'part_accessory_fitment_rel', 'fitment_id', 'product_id', string='Parts and Accessories',
        domain=lambda self: [('details_model', 'in', ['product.template.details', 'accessories'])])
    standard_jobs_ids = fields.Many2many(
        'service.standard_job', 'standard_job_fitment_rel', 'fitment_id', 'product_id', string='Standard Jobs')
    make_attr_value_id = fields.Many2one(
        'product.attribute.value', string='Vehicle Make', required=True,
        domain=lambda self: [('attribute_id', '=', self.env.ref(self._product_attribute_make).id)])
    model_attr_value_id = fields.Many2one(
        'product.attribute.value', string='Vehicle Model',
        domain=lambda self: [('attribute_id', '=', self.env.ref(self._product_attribute_model).id)])
    year_attr_value_ids = fields.Many2many(
        'product.attribute.value', string='Vehicle Years',
        domain=lambda self: [('attribute_id', '=', self.env.ref(self._product_attribute_year).id)])

    # @api.onchange('type')
    # def _onchange_type(self):
    #     if self.type == 'product':
    #         self.standard_jobs_ids = None
    #     else:
    #         self.part_accessory_ids = None

    @api.onchange('make_attr_value_id')
    def _onchange_make_attr_value_id(self):
        if self.make_attr_value_id:
            self.model_attr_value_id = None
            allowed_models = self.make_attr_value_id.product_ids.mapped('attribute_value_ids').filtered(
                lambda r: r.attribute_id == r.env.ref(self._product_attribute_model))
            return {'domain': {'model_attr_value_id': [('id', 'in', allowed_models.ids)]}}

    def get_vehicles_domain(self):
        domain = list()
        if self.make_attr_value_id:
            domain.append(('attribute_value_ids', 'in',
                           self.make_attr_value_id.ids))
        if self.model_attr_value_id:
            domain.append(('attribute_value_ids', 'in',
                           self.model_attr_value_id.ids))
        if self.year_attr_value_ids:
            domain.append(('attribute_value_ids', 'in',
                           self.year_attr_value_ids.ids))
        return domain

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'product.fitment') or 'New'
        result = super(Fitment, self).create(vals)
        return result

    def get_fitment_by_make_model_year(self, make=None, model=None, year=None):
        domain = list()
        if make:
            domain.append(('make_attr_value_id', '=', make))
        if model:
            domain.append(('model_attr_value_id', '=', model))
        if year:
            domain.append(('year_attr_value_ids', '=', year))
        fitments = self.search(domain) if domain else None
        return fitments
