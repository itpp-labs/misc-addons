# -*- coding: utf-8 -*-
# Copyright 2017 Dinar Gabbasov <https://www.it-projects.info/team/GabbasovDinar>
# Copyright 2018 Rafis Bikbov <https://www.it-projects.info/team/RafiZz>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields
import mimetypes
import requests

from odoo import fields
from odoo.tools.mimetypes import guess_mimetype
from . import image


def get_mimetype_and_optional_content_by_url(url):
    mimetype = mimetypes.guess_type(url)[0]
    content = None

    # head request for content-type header getting
    if not mimetype:
        with requests.head(url) as r:
            mimetype = getattr(r, 'headers', {}).get('Content-Type')

    index_content = mimetype and mimetype.split('/')[0]
    if not mimetype or index_content == 'text':
        with requests.get(url) as r:
            content = getattr(r, 'content')
            if not mimetype and content:
                mimetype = guess_mimetype(content)

    return mimetype, content


class Binary(fields.Binary):

    def write(self, records, value, create=False):
        domain = [
            ('res_model', '=', records._name),
            ('res_field', '=', self.name),
            ('res_id', 'in', records.ids),
        ]
        atts = records.env['ir.attachment'].sudo().search(domain)
        if value and atts.url and atts.type == 'url' and not image.is_url(value):
            atts.write({
                'url': None,
                'type': 'binary',
            })
        if value and image.is_url(value):
            with records.env.norecompute():
                if value:
                    mimetype, content = get_mimetype_and_optional_content_by_url(value)
                    index_content = records.env['ir.attachment']._index(content, None, mimetype)

                    # update the existing attachments
                    atts.write({
                        'url': value,
                        'mimetype': mimetype,
                        'datas': None,
                        'type': 'url',
                        'index_content': index_content,
                    })

                    # create the missing attachments
                    for record in (records - records.browse(atts.mapped('res_id'))):
                        atts.create({
                            'name': self.name,
                            'res_model': record._name,
                            'res_field': self.name,
                            'res_id': record.id,
                            'type': 'url',
                            'url': value,
                            'mimetype': mimetype,
                            'index_content': index_content,
                        })
                else:
                    atts.unlink()
        else:
            super(Binary, self).write(records, value, create=create)


fields.Binary = Binary
