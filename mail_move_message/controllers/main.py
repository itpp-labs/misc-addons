from openerp.addons.web.controllers.main import DataSet
from openerp.tools.translate import _
from openerp import http
from openerp.http import request

class DataSetCustom(DataSet):

    def _extend_name(self, model, records):
        cr, uid, context = request.cr, request.uid, request.context
        Model = request.registry[model]
        fields = Model.fields_get(cr, uid, False, context)
        contact_field = False
        for n, f in fields.iteritems():
            if f['type'] == 'many2one' and f['relation'] == 'res.partner':
                contact_field = n
                break
        partner_info = {}
        if contact_field:
            partner_info = Model.read(cr, uid, [r[0] for r in records], [contact_field], context)
            partner_info = dict([(p['id'], p[contact_field]) for p in partner_info])
        res = []
        for r in records:
            if partner_info.get(r[0]):
                res.append((r[0], _('%s [%s] ID %s') % (r[1], partner_info.get(r[0])[1], r[0])))
            else:
                res.append((r[0], _('%s ID %s') % (r[1], r[0])))
        return res


    @http.route('/web/dataset/call_kw/<model>/name_search', type='json', auth="user")
    def name_search(self, model, method, args, kwargs):
        context = kwargs.get('context')
        if context and context.get('extended_name_with_contact'):
            #add order by ID desc
            cr, uid = request.cr, request.uid
            Model = request.registry[model]
            search_args = list(kwargs.get('args') or [])
            limit = int(kwargs.get('limit') or 100)
            operator = kwargs.get('operator')
            name = kwargs.get('name')
            if Model._rec_name and (not name == '' and operator == 'ilike'):
                search_args += [(Model._rec_name, operator, name)]
            ids = Model.search(cr, uid, search_args, limit=limit, order='id desc', context=context)
            res = Model.name_get(cr, uid, ids, context)
            return self._extend_name(model, res)

        return self._call_kw(model, method, args, kwargs)

    @http.route('/web/dataset/call_kw/<model>/name_get', type='json', auth="user")
    def name_get(self, model, method, args, kwargs):
        res = self._call_kw(model, method, args, kwargs)
        context = kwargs.get('context')
        if context and context.get('extended_name_with_contact'):
            res = self._extend_name(model, res)
        return res
