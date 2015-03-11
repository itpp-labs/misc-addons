from openerp import api, models, fields, SUPERUSER_ID


class crm_phonecall(models.Model):
    _inherit = "crm.phonecall"

    repair_id = fields.Many2one('mrp.repair', 'Repair Order')


class mrp_repair(models.Model):
    _inherit = 'mrp.repair'

    @api.one
    def _get_phonecall_count(self):
        self.phonecall_count = self.env['crm.phonecall'].search_count([('repair_id', '=', self.id)])

    phonecall_count = fields.Integer('Phonecalls Count', compute='_get_phonecall_count')
