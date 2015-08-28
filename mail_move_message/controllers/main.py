from openerp.addons.web.controllers.main import DataSet
from openerp.tools.translate import _
from openerp.http import request

class DataSetCustom(DataSet):

    def _call_kw(self, model, method, args, kwargs):
        res = super(DataSetCustom, self)._call_kw(model, method, args, kwargs)
        if method == 'name_search' and 'context' in kwargs and kwargs['context'].get('extended_name_with_contact') and res:
            model = request.session.model(model)
            fields = model.fields_get(False, request.context)
            contact_field = False
            for n, f in fields.iteritems():
                if f['type'] == 'many2one' and f['relation'] == 'res.partner':
                    contact_field = n
                    break
            partner_info = {}
            if contact_field:
                partner_info = model.read([r[0] for r in res], [contact_field])
                partner_info = dict([(p['id'], p[contact_field]) for p in partner_info])
            final_res = []
            for r in res:
                if partner_info.get(r[0]):
                    final_res.append((r[0], _('%s [partner: %s] ID %s') % (r[1], partner_info.get(r[0])[1], r[0])))
                else:
                    final_res.append((r[0], _('%s ID %s') % (r[1], r[0])))
            res = final_res
        return res
        

