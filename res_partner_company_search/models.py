# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    p_category_id = fields.Many2many('res.partner.category', related='parent_id.category_id', string='Parent Tags')
    p_user_id = fields.Many2one('res.users', related='parent_id.user_id', string='Parent Salesperson')
    p_email = fields.Char(related='parent_id.email', string='Parent Email')
    p_phone = fields.Char(related='parent_id.phone', string='Parent Phone')
    p_fax = fields.Char(related='parent_id.fax', string='Parent Fax')

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        if not (context and context.get('parent_search_applied')):
            # update search domain:
            # [..., ('category_id', OPERATOR, VALUE), ...] ->
            # [..., '|', ('p_category_id', OPERATOR, VALUE), ('category_id', OPERATOR, VALUE), ...]
            parent_args = []
            for a in args:
                if isinstance(a, (list, tuple)) and 'p_%s' % a[0] in self._fields:
                    new_a = list(a[:])  # create copy and convert to list
                    new_a[0] = 'p_%s' % a[0]
                    parent_args.append('|')
                    parent_args.append(new_a)
                parent_args.append(a)
            args = parent_args
            context = (context or {}).copy()
            context['parent_search_applied'] = 1

        return super(ResPartner, self).search(cr, user, args, offset=offset, limit=limit, order=order, context=context, count=count)
