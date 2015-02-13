from openerp import api,models,fields

class product_style(models.Model):
    _inherit = "product.style"

    name = fields.Char(translate=True)
    auto = fields.Boolean('Auto style', default=False)
    can_be_ordered = fields.Boolean('Can be ordered', default=True)

class product_template(models.Model):
    _inherit = 'product.template'

    @api.model
    def update_stock_status_all(self):
        ribbon_backordered = self.env.ref("website_sale_stock_status.ribbon_backordered").id
        ribbon_discontinued = self.env.ref("website_sale_stock_status.ribbon_discontinued").id
        # 3 - unlink, 4 - link
        self.search([('qty_available', '>', 0)]).write({'website_style_ids':[(3, ribbon_backordered, 0), (3, ribbon_discontinued, 0)]})
        self.search([('qty_available', '=', 0), ('state', 'in', ['end', 'obsolete'])]).write({'website_style_ids':[(3, ribbon_backordered, 0), (4, ribbon_discontinued, 0)]})
        self.search([('qty_available', '=', 0), ('state', 'not in', ['end', 'obsolete'])]).write({'website_style_ids':[(4, ribbon_backordered, 0), (3, ribbon_discontinued, 0)]})
