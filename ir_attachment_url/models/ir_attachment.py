# -*- coding: utf-8 -*-
import requests
import base64
from openerp import api, models
import openerp

# To avoid travis warnings
osv = openerp.osv.osv
fields = openerp.osv.fields


class IrAttachment(osv.osv):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment']

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        return super(IrAttachment, self)._data_set(cr, uid, id, name, value, arg, context=context)

    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        bin_size = context.get('bin_size')
        ordinary_ids = []
        for attach in self.browse(cr, uid, ids, context=context):
            if attach.type == 'url' and attach.url:
                if not bin_size:
                    response = requests.get(attach.url)
                    result[attach.id] = base64.b64encode(response.content)
                else:
                    result[attach.id] = "1.00 Kb"
            else:
                ordinary_ids.append(attach.id)
        result.update(super(IrAttachment, self)._data_get(cr, uid, ordinary_ids, name, arg, context=context))
        return result

    _columns = {
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
    }


class IrAttachmentNewApi(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    def _filter_protected_attachments(self):
        return self.filtered(lambda r: r.res_model != 'ir.ui.view' or not r.name.startswith('/web/content/'))
