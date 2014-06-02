# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _

class res_partner(osv.Model):
    _inherit = "res.partner"

    _columns = {
        'site_customer': fields.boolean('Сайт')
    }
    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        if context and context.has_key('hacked_global_search'):
            #args = [['customer', '=', 1], '|', '|', ['name', 'ilike', u'\u0444'], ['parent_id', 'ilike', u'\u0444'], ['ref', '=', u'\u0444']]

            check = {'name':False, 'parent_id':False, 'ref':False}
            for a in args:
                if type(a) == list and len(a)==3 and (a[0] in check):
                    try:
                        check[a[0]] = len(a[2]) >= 3
                    except:
                        pass
            do_global_search = True
            for c in check:
                do_global_search = do_global_search and check[c]
            if do_global_search:
                user = SUPERUSER_ID
            else:
                del context['hacked_global_search']
        res = super(res_partner, self).search(cr, user, args, offset, limit, order, context, count)
        return res

    def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
        if context and context.has_key('hacked_global_search'):
            user = SUPERUSER_ID
            #del context['hacked_global_search']
        res = super(res_partner, self).read(cr, user, ids, fields, context, load)
        return res

class control_site_customer(osv.TransientModel):
    _name = 'security_sarrz.control_site_customer'
    _columns = {
        #'value': fields.selection([('mark', 'Отметить'), ('unmark', 'Снять отметку'),], 'Новое значение поля Сайт'),
    }
    def _do(self, cr, uid, ids, value, context=None):
        active_ids = context.get('active_ids') or []
        cr.execute("""UPDATE res_partner
                      set site_customer=%s
                      WHERE id IN %s
        """, (value,tuple(active_ids)))

    def mark(self, cr, uid, ids, context=None):
        self._do(cr, uid, ids, True, context)
    def unmark(self, cr, uid, ids, context=None):
        self._do(cr, uid, ids, False, context)
