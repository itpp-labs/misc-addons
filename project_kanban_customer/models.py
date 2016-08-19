# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    partner_country_image = fields.Binary('Partner\'s country flag', related='partner_id.country_id.image')
    partner_country_name = fields.Char('Partner\'s country name', related='partner_id.country_id.name')

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['partner_id', 'name'], context=context)
        res = []
        for record in reads:
            name = record['name'] or ''
            partner = record['partner_id'] or ''
            if partner:
                name = '%s (%s)' % (name, partner[1])
            res.append((record['id'], name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            ids = self.search(cr, uid, ['|', ('partner_id', operator, name), ('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)
