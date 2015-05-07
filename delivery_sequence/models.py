from openerp import api, models, fields, SUPERUSER_ID


class delivery_carrier(models.Model):
    _inherit = "delivery.carrier"

    _order = 'sequence,id'

    sequence = fields.Integer('Sequence', default=0)
