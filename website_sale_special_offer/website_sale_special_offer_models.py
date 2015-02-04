from openerp import api,models,fields,SUPERUSER_ID,exceptions
import openerp.addons.decimal_precision as dp
from openerp.osv import osv, orm, fields as old_fields
from openerp.addons.web.http import request

class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    special_offer_line_id = fields.Many2one('website_sale_special_offer.special_offer.line', string='Special offer Line')

    def _get_price_total(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total_included'])
        return res

    _columns = {
        'price_total': old_fields.function(_get_price_total, string='Total', digits_compute= dp.get_precision('Account')),
    }

class sale_order(models.Model):
    _inherit = "sale.order"

    def _cart_update(self, cr, uid, ids, product_id=None, line_id=None, add_qty=None, set_qty=None, context=None,
                     # new stuff:
                     update_existed=True,
                     special_offer_line=None,
                     **kwargs):
        """ Add or set product quantity, add_qty can be negative
        (based on addons/website_sale/models/sale_order.py::_cart_update)
 """
        sol = self.pool.get('sale.order.line')
        for so in self.browse(cr, uid, ids, context=context):
            quantity = 0
            line = None
            if line_id != False:
                line_ids = so._cart_find_product_line(product_id, line_id, context=context, **kwargs)
                if line_ids:
                    line_id = line_ids[0]
            if line_id:
                line = sol.browse(cr, SUPERUSER_ID, line_id, context=context)
            if line and line.special_offer_line_id and not update_existed:
                quantity = line.product_uom_qty
                return {'line_id': line_id, 'quantity': quantity}

            # Create line if no line with product_id can be located
            if not line_id:
                values = self._website_product_id_change(cr, uid, ids, so.id, product_id, qty=1, context=context)
                line_id = sol.create(cr, SUPERUSER_ID, values, context=context)
                line = sol.browse(cr, SUPERUSER_ID, line_id, context=context)
                if add_qty:
                    add_qty -= 1
            sline = special_offer_line or line.special_offer_line_id
            # compute new quantity
            if set_qty or set_qty != None and sline:
                quantity = set_qty
            elif add_qty != None:
                quantity = sol.browse(cr, SUPERUSER_ID, line_id, context=context).product_uom_qty + (add_qty or 0)

            # Remove zero of negative lines
            if quantity < 0:
                quantity=0
            if sline and sline.mandatory and quantity < sline.product_uom_qty:
                quantity = sline.product_uom_qty
            if quantity <= 0 and not sline:
                sol.unlink(cr, SUPERUSER_ID, [line_id], context=context)
            else:
                # update line
                values = self._website_product_id_change(cr, uid, ids, so.id, product_id, qty=quantity, line_id=line_id, context=context)
                values['product_uom_qty'] = quantity
                if sline:
                    values['special_offer_line_id'] = sline.id
                    values['price_unit'] = sline.price_unit
                sol.write(cr, SUPERUSER_ID, [line_id], values, context=context)

            so.update_special_offer_rules()

        return {'line_id': line_id, 'quantity': quantity}

    @api.one
    def update_special_offer_rules(self):
        for line in self.order_line:
            if line.discount:
                line.discount = 0
        amount_total = self.amount_total
        items = dict( (line.product_id.id, line.product_uom_qty) for line in self.order_line)
        sort = lambda line: 0 if not (line.special_offer_line_id and line.special_offer_line_id.rule_id) else {'free_when_others_ordered': 1, 'free_when_over':2}[line.special_offer_line_id.rule_id.type]

        for line in sorted(self.order_line, key=sort):
            sline = line.special_offer_line_id
            rule = sline and sline.rule_id
            if not rule:
                continue

            free_quantity = sline.rule_quantity or 1
            if rule.type == 'free_when_over':
                discount_total = free_quantity * sline.price_unit
                if amount_total -  discount_total < rule.value:
                    free_quantity = 0
            elif rule.type == 'free_when_others_ordered':
                for r in rule.product_ids:
                    id = r.product_id.id
                    if id not in items or items[id] < r.product_uom_qty:
                        free_quantity = 0
                        break

            if free_quantity:
                line_total = line.product_uom_qty * sline.price_unit
                discount_total = free_quantity * sline.price_unit
                discount = 100
                if line_total > discount_total:
                    discount = 100 * discount_total/line_total
                line.discount = discount
            else:
                line.discount = 0

class website_sale_special_offer(models.Model):
    _name = 'website_sale_special_offer.special_offer'
    _description = 'Special offer'

    name = fields.Char('Name')
    title = fields.Char('Title', help="Title to show at website", default="Special offer")
    url = fields.Char('URL', help="e.g. kits")
    page_content0 = fields.Html("Content 0")
    page_content1 = fields.Html("Content 1")
    page_content2 = fields.Html("Content 2")
    page_content3 = fields.Html("Content 3")
    line_ids = fields.One2many('website_sale_special_offer.special_offer.line', 'special_offer_id', string='Lines')
    active = fields.Boolean('Active')

    @api.model
    def check_urls(self, vals):
        NOT_ALLOWED_URLS = ['web', 'shop', 'page']
        if 'url' in vals:
            if vals['url']:
                vals['url'] = vals['url'].strip()
            if vals['url'] in NOT_ALLOWED_URLS:
                raise exceptions.Warning('You cannot use these urls: %s' % ', '.join(NOT_ALLOWED_URLS))

    @api.multi
    def write(self, vals):
        self.check_urls(vals)
        return super(website_sale_special_offer, self).write(vals)

    @api.model
    def create(self, vals):
        self.check_urls(vals)
        return super(website_sale_special_offer, self).create(vals)

class website_sale_special_offer_line(models.Model):
    _name = 'website_sale_special_offer.special_offer.line'

    name = fields.Char('Name')
    special_offer_id = fields.Many2one('website_sale_special_offer.special_offer', string='Special offer')
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_qty = fields.Integer('Init Quantaty', help='Init value for product')
    mandatory = fields.Boolean('Mandatory', help='Init quantaty of a product cannot be decreased')
    price_unit = fields.Float('Unit price', required=True)
    rule_id = fields.Many2one('website_sale_special_offer.special_offer.line.rule', string='Rule')
    rule_quantity = fields.Integer('Quantaty for rule', help='E.g. how much free items when some condition is passed')
    sequence = fields.Integer('Sequence')

class website_sale_special_offer_line_rule(models.Model):
    _name = 'website_sale_special_offer.special_offer.line.rule'

    name = fields.Char('Name')
    description = fields.Char('Description', help='Hint to show in a order line. E.g. "Free when ordering over 50$"')
    type = fields.Selection(selection=[
        ('free_when_over', 'Free when over'),
        ('free_when_others_ordered', 'Free when others ordered')
    ], string='Type')
    value = fields.Float('Value', help='meaning depends on type of rule')
    product_ids = fields.One2many('website_sale_special_offer.special_offer.line.rule.p', 'rule_id', string='Products')

class website_sale_special_offer_line_rule_p(models.Model):
    _name = 'website_sale_special_offer.special_offer.line.rule.p'

    rule_id = fields.Many2one('website_sale_special_offer.special_offer.line.rule', string='Rule')
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_qty = fields.Integer('Quantaty', help='Init value for product')


class Website(orm.Model):
    _inherit = 'website'

    def sale_product_domain(self, cr, uid, ids, context=None):
        return ['&'] + super(Website, self).sale_product_domain(cr, uid, ids, context=context) + [('special_offer_ok', '=', False)]


class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
        'special_offer_ok': old_fields.boolean('Special offer only', help='Hide product from /shop directory.'),
    }
    _defaults = {
        'special_offer_ok': False,
    }



class website(orm.Model):
    _inherit = 'website'

    def sale_reset(self, cr, uid, ids, context=None):
        order = request.website.sale_get_order()
        if order:
            for line in order.website_order_line:
                if not line.product_uom_qty:
                    line.unlink()
        return super(website, self).sale_reset(cr, uid, ids, context=context)
