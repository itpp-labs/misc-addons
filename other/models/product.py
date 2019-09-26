from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _model_selection(self):
        selection = super(ProductTemplate, self)._model_selection()
        selection.append(('other', 'Other'))
        return selection
