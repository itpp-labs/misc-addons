# -*- coding: utf-8 -*-
from openerp.osv import fields
from openerp import SUPERUSER_ID
import mimetypes
from . import image


super_binary_set = fields.binary.set


def set(self, cr, obj, id, name, value, user=None, context=None):
        domain = [
            ('res_model', '=', obj._name),
            ('res_field', '=', name),
            ('res_id', '=', id),
        ]

        atts = obj.pool['ir.attachment'].browse(cr, SUPERUSER_ID, [], context).search(domain)

        if value and atts.url and atts.type == 'url' and not image.is_url(value):
            atts.write({
                'url': None,
                'type': 'binary',
            })
        if value and image.is_url(value):
            with atts.env.norecompute():
                if value:
                    if atts:
                        # update the existing attachments
                        atts.write({
                            'url': value,
                            'mimetype': mimetypes.guess_type(value)[0],
                            'datas': None,
                            'type': 'url',
                        })
                    else:
                        atts.create({
                            'name': name,
                            'res_model': obj._name,
                            'res_field': name,
                            'res_id': id,
                            'type': 'url',
                            'url': value,
                        })
                else:
                    atts.unlink()
            return []
        else:
            return super_binary_set(self, cr, obj, id, name, value, user, context)

fields.binary.set = set
