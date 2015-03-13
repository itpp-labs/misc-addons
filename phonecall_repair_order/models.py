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

    def name_get(self, cr, uid, ids, context=None):
        #if not (context or {}).get('mrp_repair_extended_name'):
        #    return super(mrp_repair, self).name_get(cr, uid, ids, context=context)

        res = []
        for r in self.browse(cr, uid, ids, context=context):
            name = '%s [%s]' % (r.name, r.partner_id.display_name)
            res.append((r.id, name))
        return res
