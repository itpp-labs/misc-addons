from odoo import api, fields, models


def _compose_vehicle_product_name(product):
    if product.details_model in ['vehicle', 'nadanew.vehicle.product']:
        if any(product.get_year_make_model()):
            return product.get_stripped_year_make_model()


def no_connector_export(context):
    return (context.get('no_connector_export') or
            context.get('connector_no_export'))


class ProductTemplate(models.Model):
    _inherit = "product.template"

    major_unit_qty = fields.Integer(string="Major Units Quantity", compute='_compute_major_unit_qty', store=True)
    list_price = fields.Float(default=0.0)

    def _model_selection(self):
        selection = super(ProductTemplate, self)._model_selection()
        # selection.append(('vehicle', 'Vehicle'))
        return selection

    @api.multi
    @api.depends('product_variant_ids', 'product_variant_ids.major_unit_qty', 'details_model', 'attribute_line_ids')
    def _compute_major_unit_qty(self):
        for record in self:
            record.major_unit_qty = sum([product.major_unit_qty for product in self.mapped('product_variant_ids')])

    @api.onchange('details_model', 'attribute_line_ids')
    def _compute_product_product_name(self):
        composed_name = _compose_vehicle_product_name(self)
        if composed_name:
            self.name = composed_name

    @api.multi
    def action_open_major_units(self):
        prod_lots_ids = list()
        for product in self.product_variant_ids:
            prod_lots_ids.extend([lot.id for lot in product.prod_lot_ids])
        action = self.env.ref('major_unit.open_major_units').read()[0]
        action['domain'] = [('prod_lot_id', 'in', prod_lots_ids)]
        return action

    @api.multi
    def write(self, vals):
        if len(self) == 1:
            composed_name = _compose_vehicle_product_name(self)
            if composed_name:
                vals['name'] = composed_name
        res = super(ProductTemplate, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        self.set_default_category_by_details_model(vals)
        if not vals.get('name') and self.env.context.get('name'):
            vals['name'] = self.env.context.get('name')
        product = super(ProductTemplate, self).create(vals)
        return product

    @api.model
    def _get_year_make_model(self):
        attribute_value_ids = self.mapped('attribute_line_ids')
        year = attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_year))
        make = attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_make))
        model = attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_model))
        return year, make, model

    def get_year_make_model(self):
        year, make, model = self._get_year_make_model()

        year = year and year[0].value_ids
        year = year and len(year) == 1 and year.name or ''

        make = make and make[0].value_ids
        make = make and len(make) == 1 and make.name or ''

        model = model and model[0].value_ids
        model = model and len(model) == 1 and model.name or ''

        return year, make, model

    def get_stripped_year_make_model(self):
        return ("%s %s %s" % (self.get_year_make_model())).strip()

    def _get_default_category_by_details_model(self, details_model):
        default_category_maps = {
            'product.template.details': 'drm_product_attributes.product_category_parts',
            'accessories': 'drm_product_attributes.product_category_accessories',
            'apparel': 'drm_product_attributes.product_category_apparel',
        }
        category_xml_id = default_category_maps.get(details_model)
        return category_xml_id and self.env.ref(category_xml_id, raise_if_not_found=False)

    def set_default_category_by_details_model(self, vals):
        details_model = vals.get('details_model')
        categ_id = vals.get('categ_id')
        if details_model and categ_id == self.env.ref('product.product_category_all').id:
            category = self._get_default_category_by_details_model(details_model)
            if category:
                vals['categ_id'] = category.id


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _default_name(self):
        name = self.get_stripped_year_make_model()
        if self.product_tmpl_id:
            return self.product_tmpl_id.name
        return name

    name = fields.Char('Name', required=True, index=True, translate=True, default=_default_name)
    major_unit_qty = fields.Integer(string="Major Units Quantity", compute='_compute_major_unit_qty', store=True)
    prod_lot_ids = fields.One2many('stock.production.lot', 'product_id')
    fitment_ids = fields.Many2many('product.fitment', 'part_accessory_fitment_rel', 'product_id', 'fitment_id')

    @api.multi
    @api.depends('prod_lot_ids', 'prod_lot_ids.major_unit_ids')
    def _compute_major_unit_qty(self):
        for record in self:
            record.major_unit_qty = len(record.prod_lot_ids.filtered('major_unit_ids'))

    @api.onchange('details_model', 'attribute_value_ids')
    def _compute_product_product_name(self):
        self.name = self.name or self.product_tmpl_id.name
        composed_name = _compose_vehicle_product_name(self)
        if composed_name:
            self.name = composed_name

    @api.multi
    def write(self, vals):
        if len(self) == 1:
            composed_name = _compose_vehicle_product_name(self)
            if composed_name:
                vals['name'] = composed_name
        res = super(ProductProduct, self).write(vals)
        if no_connector_export(self.env.context):
            for record in self:
                record.update_prices_for_related_tmpl()
                record.set_details_part_number_for_related_tmpl()
                record.add_tracking_to_vehicle()
                record.create_major_unit_for_vehicles()
                record.set_price_extra_attr_by_tmpl()
        return res

    @api.model
    def create(self, vals):
        if no_connector_export(self.env.context):
            self.check_unique_barcode(vals)

        product = super(ProductProduct, self.with_context(create_product_product=True, name=vals.get('name'))).create(vals)
        name = product.get_stripped_year_make_model()
        if self.env.context.get('create_from_tmpl'):
            product.name = name or vals.get('name', False) or product.product_tmpl_id.name
        if not product.name:
            product.name = vals.get('name', False) or name or product.product_tmpl_id.name
        composed_name = _compose_vehicle_product_name(product)
        if composed_name:
            product.name = composed_name
        if no_connector_export(self.env.context):
            product.update_prices_for_related_tmpl()
            product.set_price_extra_attr_by_tmpl()
        return product

    @api.multi
    def action_open_major_units(self):
        prod_lots = self.mapped('prod_lot_ids')
        action = self.env.ref('major_unit.open_major_units').read()[0]
        action['domain'] = [('prod_lot_id', 'in', prod_lots.ids)]
        return action

    @api.model
    def _get_year_make_model(self):
        year = self.attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_year))
        make = self.attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_make))
        model = self.attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_model))
        return year, make, model

    @api.multi
    def action_open_parts_accessories(self):
        year, make, model = self._get_year_make_model()
        record_ids = self.get_parts_accessories(make=make.id, model=model.id, year=year.id)
        action = self.env.ref('major_unit.open_parts_accessories').read()[0]
        action['domain'] = [('id', 'in', record_ids.ids)]
        return action

    def get_parts_accessories(self, product_type=None, make=None, model=None, year=None):
        """ The function allows get parts and accessories suitable for a vehicle by make, model, year parameters.
        Also the function returns generic parts and accessories are have not fitment records.
        :param str product_type: optional, one of 'product.template.details', 'accessories'. By default, both types.
        :param int make: optional, record id of make attribute value
        :param int model: optional, record id of model attribute value
        :param  int year: optional, record id of year attribute value
        :return: recordset: a recordset of products
        """
        product_types_valid = details_model = ['product.template.details', 'accessories']
        if product_type:
            if product_type not in product_types_valid:
                raise ValueError(
                    'Cannot get products with type %s. Valid types: %s'
                    % (product_type, ', '.join(product_types_valid)))
            else:
                details_model = [product_type]
        domain = [('details_model', 'in', details_model)]
        fitments = self.env['product.fitment'].get_fitment_by_make_model_year(make, model, year)
        if fitments:
            domain.append(('fitment_ids', 'in', fitments.ids))
        products = self.search(domain)
        return products

    @api.multi
    def action_open_vehicles(self):
        action = self.env.ref('major_unit.open_vehicles').read()[0]
        domain = [('details_model', 'in', ['vehicle', 'nadanew.vehicle.product'])]
        fitment_count = len(self.fitment_ids)
        if fitment_count:
            domain += [('|')] * (fitment_count - 1)
            extra_domain = list()
            for fitment in self.fitment_ids:
                extra_domain += fitment.get_vehicles_domain()
            domain += extra_domain
        else:
            year, make, model = self._get_year_make_model()
            if make:
                domain.append(('attribute_value_ids', 'in', make.ids))
                if model:
                    domain.append(('attribute_value_ids', 'in', model.ids))
                    if year:
                        domain.append(('attribute_value_ids', 'in', year.ids))
        action['domain'] = domain
        return action

    def get_year_make_model(self):
        year, make, model = self._get_year_make_model()

        year = len(year) == 1 and year.name or ''
        make = len(make) == 1 and make.name or ''
        model = len(model) == 1 and model.name or ''

        return year, make, model

    def get_stripped_year_make_model(self):
        return ("%s %s %s" % (self.get_year_make_model())).strip()

    @api.multi
    def update_prices_for_related_tmpl(self):
        tmpl_price_fields_mapped_to_product = {
            'minap': 'minap',
            'msrp': 'msrp',
            'list_price': 'minap',
        }
        for record in self:
            tmpl = record.product_tmpl_id
            if hasattr(self.env['product.product'], 'regular_price') and \
                    hasattr(self.env['product.template'], 'regular_price'):
                tmpl_price_fields_mapped_to_product.update({'regular_price': 'regular_price'})

            for tmpl_field, prod_field in tmpl_price_fields_mapped_to_product.items():
                variant_prod_field_not_null_values = [float(v) for v in tmpl.product_variant_ids.filtered(lambda r: r[prod_field]).mapped(prod_field)]
                if variant_prod_field_not_null_values:
                    tmpl[tmpl_field] = min(variant_prod_field_not_null_values)

    @api.multi
    def set_price_extra_attr_by_tmpl(self):
        price_extra_attr = self.env.ref('drm_product_attributes.product_attribute_price_extra')
        for record in self.mapped('product_tmpl_id.product_variant_ids'):
            price_extra = record.minap - record.list_price
            price_attr = self.env['product.attribute.price'].search([
                ('product_tmpl_id', '=', record.product_tmpl_id.id),
                ('value_id.product_ids', '=', record.id),
            ])

            if not price_extra:
                price_attr.value_id.unlink()
                price_attr.unlink()
                continue

            attr_name = 'ID{} ({})'.format(record.id, round(price_extra, 2) or price_extra)
            if price_attr:
                price_attr.price_extra = price_extra
                price_attr.value_id.name = attr_name
            else:
                product_attribute_value = record.attribute_value_ids.filtered(lambda r: r.attribute_id == price_extra_attr)
                if product_attribute_value:
                    product_attribute_value.name = attr_name
                else:
                    product_attribute_value = self.env['product.attribute.value'].create({
                        'name': attr_name,
                        'product_ids': [(6, 0, [record.id])],
                        'attribute_id': price_extra_attr.id,
                    })
                price_attr.create({
                    'product_tmpl_id': record.product_tmpl_id.id,
                    'value_id': product_attribute_value.id,
                    'price_extra': price_extra,
                })

    @api.multi
    def set_details_part_number_for_related_tmpl(self):
        for record in self:
            if not record.details_model == 'product.template.details':
                continue

            product_template = record.product_tmpl_id
            if product_template.details and product_template.details.part_number:
                continue

            details_record = self.env['product.template.details'].create({
                'part_number': record.sku,
                'part_reference_number': '',
            })
            product_template.write({
                'details_model_record': 'product.template.details,{}'.format(details_record.id),
                'details_model_exists': True,
                'details_res_id': details_record.id,
            })

    @api.model
    def check_unique_barcode(self, vals):
        barcode = vals.get('barcode')
        if not barcode:
            if 'barcode' in vals:
                del vals['barcode']
            return
        barcode_prefix = '$'
        while self.search_count([('barcode', '=', barcode)]):
            barcode = '{}{}'.format(barcode_prefix, barcode)
        vals['barcode'] = barcode

    def add_tracking_to_vehicle(self):
        for record in self:
            if record.details_model in ['vehicle', 'nadanew.vehicle.product'] and \
                    record.tracking == 'none':
                record.tracking = 'serial'

    def create_major_unit_for_vehicles(self):
        major_unit = self.env['major_unit.major_unit']
        stock_prod_lot = self.env['stock.production.lot']
        for record in self:
            if record.details_model in ['vehicle', 'nadanew.vehicle.product'] and \
                    not major_unit.search([('prod_lot_id.product_id', '=', record.id)]):
                prod_lot = stock_prod_lot.create({
                    'product_id': record.id,
                })
                major_unit.create({
                    'prod_lot_id': prod_lot.id,
                })


class ProductImage(models.Model):
    _name = 'product.image'
    _inherit = ['product.image', 'web.preview']

    _preview_media_file = 'image'
