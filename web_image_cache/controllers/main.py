# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2019 Alexandr Kolushov <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019-2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

import base64
import logging

from odoo.http import request

from odoo.addons.web.controllers.main import Binary

_logger = logging.getLogger(__name__)


class BinaryExtended(Binary):
    def _content_image(self, **kw):
        """
        Overrided content_image checks, if is resized image already created
        if yes - return it
        if no - store and return it
        """
        env = request.env
        xmlid = kw.get("xmlid", None)
        model = kw.get("model", "ir.attachment")
        id = kw.get("id")  # pylint: disable=redefined-builtin
        field = kw.get("field", "datas")
        width = int(kw.get("width", 0))
        height = int(kw.get("height", 0))
        crop = kw.get("crop", False)
        access_token = kw.get("access_token", None)
        # TODO: add quality

        if not (width or height):
            # image is definately won't be resized
            _logger.debug("Image not gonna be be resized")
            return super(BinaryExtended, self)._content_image(**kw)

        record, status = env["ir.http"]._get_record_and_check(
            xmlid, model, id, field, access_token
        )

        if not record:
            return super(BinaryExtended, self)._content_image(**kw)

        if not record._fields[field].attachment:
            _logger.debug(
                "Field {} on model {} is not stored as attachment".format(field, model)
            )
            return super(BinaryExtended, self)._content_image(**kw)

        related = record._fields[field].related
        if related and len(related) >= 2:
            related = record._fields[field].related
            new_record = record[related[0]]
            kw["id"] = new_record.id
            kw["model"] = new_record._name
            kw["field"] = related[1]
            kw.pop("xmlid", None)
            _logger.debug(
                "Field {} on model {} is related to {}".format(
                    field, model, repr(related)
                )
            )
            return self._content_image(**kw)

        attachment = None
        if model == "ir.attachment":
            attachment = record
        else:
            attachment = (
                env["ir.attachment"]
                .sudo()
                .search(
                    [
                        ("res_field", "=", field),
                        ("res_model", "=", model),
                        ("res_id", "=", record.id),
                    ]
                )
            )
            if not attachment:
                _logger.debug("Field {} on {} is falsy".format(field, record))
                return super(BinaryExtended, self)._content_image(**kw)
            attachment.ensure_one()
        resized = attachment.get_resized_from_cache(width, height, crop)

        if resized:
            _logger.debug("Cache hit!")
            kw["id"] = resized.resized_attachment_id.id
            kw["model"] = "ir.attachment"
            kw["field"] = "datas"
            kw["width"] = kw["height"] = 0
            kw["crop"] = 0
            return super(BinaryExtended, self)._content_image(**kw)

        # storing resized image from response to cache
        response = super(BinaryExtended, self)._content_image(**kw)
        if response.status_code != 200:
            _logger.debug("Cache miss and not 200 status")
            return response

        _logger.debug("Cache miss and storing")
        content = b"".join(response.response)
        attachment.store_resized_to_cache(
            base64.b64encode(content), width, height, crop
        )
        return response
