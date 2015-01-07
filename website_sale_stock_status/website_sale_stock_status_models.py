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
        self.search([]).update_stock_status()

    @api.one
    def update_stock_status(self):
        website_style_ids = []
        stock = self.qty_available
        state = self.state
        ribbon_backordered = self.env.ref("website_sale_stock_status.ribbon_backordered").id
        ribbon_discontinued = self.env.ref("website_sale_stock_status.ribbon_discontinued").id
        # 3 - unlink, 4 - link
        if stock > 0:
            website_style_ids.append( (3, ribbon_backordered, 0) )
            website_style_ids.append( (3, ribbon_discontinued, 0) )
        elif state in ['end', 'obsolete']:
            website_style_ids.append( (3, ribbon_backordered, 0) )
            website_style_ids.append( (4, ribbon_discontinued, 0) )
        else:
            website_style_ids.append( (4, ribbon_backordered, 0) )
            website_style_ids.append( (3, ribbon_discontinued, 0) )
        self.website_style_ids =  website_style_ids
