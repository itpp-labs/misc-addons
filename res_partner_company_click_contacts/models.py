from openerp import api, models, fields, SUPERUSER_ID


class res_partner(models.Model):
    _inherit = "res.partner"

    record_url = fields.Char('Link to record', compute='compute_record_url')

    @api.one
    def compute_record_url(self):
        self.record_url = '#id=%s&model=%s' % (self.id, self._name)
