# Copyright 2017 Dinar Gabbasov <https://www.it-projects.info/team/GabbasovDinar>
# Copyright 2018 Rafis Bikbov <https://www.it-projects.info/team/RafiZz>
# Copyright 2019 Eugene Molotov <https://www.it-projects.info/team/em230418>
# Copyright 2020 Karl <https://github.com/theangryangel>
# License MIT (https://opensource.org/licenses/MIT).
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
        with requests.head(url, timeout=5) as r:
            mimetype = getattr(r, "headers", {}).get("Content-Type")

    index_content = mimetype and mimetype.split("/")[0]
    if not mimetype or index_content == "text":
        with requests.get(url, timeout=5) as r:
            content = r.content
            if not mimetype and content:
                mimetype = guess_mimetype(content)

    return mimetype, content


binary_original_create = fields.Binary.create
binary_original_write = fields.Binary.write


# use if-block to keep indent of previous version of the file
if True:
    # based on https://github.com/odoo/odoo/blob/bba7a6b2c46320af150f34359f742ee4e0116e66/odoo/fields.py#L1853-L1872
    def create(self, record_values):
        assert self.attachment
        if not record_values:
            return
        # create the attachments that store the values
        env = record_values[0][0].env

        # redefined part starts here
        url_record_values = []
        other_record_values = []
        for pair in record_values:
            value = pair[1]
            if image.is_url(value):
                url_record_values.append(pair)
            else:
                other_record_values.append(pair)

        with env.norecompute():
            env["ir.attachment"].sudo().with_context(
                binary_field_real_user=env.user
            ).create(
                [
                    {
                        "name": self.name,
                        "res_model": self.model_name,
                        "res_field": self.name,
                        "res_id": record.id,
                        "type": "url",  # it is not binary like in original method
                        "url": value,  # also using url field instead of datas
                    }
                    for record, value in url_record_values
                    if value
                ]
            )
        # calling original create method for non URLs
        binary_original_create(self, other_record_values)

    def write(self, records, value):
        domain = [
            ("res_model", "=", self.model_name),
            ("res_field", "=", self.name),
            ("res_id", "in", records.ids),
        ]
        atts = records.env["ir.attachment"].sudo().search(domain)
        if value and atts.url and atts.type == "url" and not image.is_url(value):
            atts.write({"url": None, "type": "binary"})
        if value and image.is_url(value):
            # save_option = records.env['ir.config_parameter'].get_param('ir_attachment_url.storage', default='url')
            with records.env.norecompute():
                # commented out some strange stuff
                # https://github.com/it-projects-llc/misc-addons/pull/775/files#r302856876
                # if value and save_option != 'url':
                #     r = requests.get(value, timeout=5)
                #     base64source = base64.b64encode(r.content)
                #     super(Binary, self).write(records, base64source)
                if value:
                    mimetype, content = get_mimetype_and_optional_content_by_url(value)
                    index_content = records.env["ir.attachment"]._index(
                        content, None, mimetype
                    )

                    # update the existing attachments
                    atts.write(
                        {
                            "url": value,
                            "mimetype": mimetype,
                            "datas": None,
                            "type": "url",
                            "index_content": index_content,
                        }
                    )

                    # create the missing attachments
                    for record in records - records.browse(atts.mapped("res_id")):
                        atts.create(
                            {
                                "name": self.name,
                                "res_model": record._name,
                                "res_field": self.name,
                                "res_id": record.id,
                                "type": "url",
                                "url": value,
                                "mimetype": mimetype,
                                "index_content": index_content,
                            }
                        )
                else:
                    atts.unlink()
        else:
            binary_original_write(self, records, value)

    fields.Binary.create = create
    fields.Binary.write = write
