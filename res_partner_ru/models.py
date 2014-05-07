# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
import werkzeug.utils
import openerp
from openerp.addons.base.ir import ir_qweb

class Contact(osv.AbstractModel):

    _inherit = 'website.qweb.field.contact'

    def record_to_html(self, cr, uid, field_name, record, column, options=None, context=None):
        opf = options.get('fields') or ["name", "address", "phone", "mobile", "fax", "email"]

        if not getattr(record, field_name):
            return None

        id = getattr(record, field_name).id
        field_browse = self.pool[column._obj].browse(cr, openerp.SUPERUSER_ID, id, context={"show_address": True})
        value = werkzeug.utils.escape( field_browse.name_get()[0][1] )

        val = {
            'name': value.split("\n")[0],
            'address': werkzeug.utils.escape("\n".join(value.split("\n")[1:])),
            'phone': field_browse.phone,
            'mobile': field_browse.mobile,
            'fax': field_browse.fax,
            'city': field_browse.city,
            'country_id': field_browse.country_id and field_browse.country_id.name_get()[0][1],
            'email': field_browse.email,
            'fields': opf,
            'options': options
        }

        # my stuff
        if 'inn_kpp' in opf:
            val.update({'inn':field_browse.inn,
                        'kpp':field_browse.kpp})

        if 'bank' in opf:
            val.update({'bank':field_browse.bank_ids[0]})
        # /my stuff

        html = self.pool["ir.ui.view"].render(cr, uid, "base.contact", val, engine='website.qweb', context=context).decode('utf8')

        return ir_qweb.HTMLSafe(html)
