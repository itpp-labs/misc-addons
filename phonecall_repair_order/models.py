# -*- coding: utf-8 -*-
from openerp import api
from openerp import fields
from openerp import models


class CrmPhonecall(models.Model):
    _inherit = "crm.phonecall"

    repair_id = fields.Many2one('mrp.repair', 'Repair Order')


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    @api.multi
    def _get_phonecall_count(self):
        for r in self:
            r._get_phonecall_count_one()
        return True

    @api.multi
    def _get_phonecall_count_one(self):
        self.ensure_one()
        self.phonecall_count = self.env['crm.phonecall'].search_count([('repair_id', '=', self.id)])

    phonecall_count = fields.Integer('Phonecalls Count', compute='_get_phonecall_count')

    def name_get(self, cr, uid, ids, context=None):
        # if not (context or {}).get('mrp_repair_extended_name'):
        #    return super(mrp_repair, self).name_get(cr, uid, ids, context=context)

        res = []
        for r in self.browse(cr, uid, ids, context=context):
            name = '%s [%s]' % (r.name, r.partner_id.display_name)
            res.append((r.id, name))
        return res
