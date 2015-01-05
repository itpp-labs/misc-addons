from openerp import api,models,fields

class product_style(models.Model):
    _inherit = "product.style"

    auto = fields.Boolean('Auto style', default=False)
