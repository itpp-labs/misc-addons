# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2019 Alexandr Kolushov <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019-2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

import base64
import logging

from odoo.exceptions import AccessError
from odoo.http import request, route
from odoo.tools import consteq

from odoo.addons.web.controllers.main import Binary

_logger = logging.getLogger(__name__)


# inspired by ir_http's _get_record_and_check from Odoo 13.0
# current's body is based on
# https://github.com/odoo/odoo/blob/f1e79c74a5c07d6be3154629f6f381ebaf907fb1/odoo/addons/base/ir/ir_http.py#L250-L298
def _get_record_and_check(
    env, xmlid=None, model=None, id=None, field="datas", access_token=None
):  # pylint: disable=redefined-builtin
    # get object and content
    obj = None
    if xmlid:
        obj = env.ref(xmlid, False)
    elif id and model in env.registry:
        obj = env[model].browse(int(id))

    # obj exists
    if not obj or not obj.exists() or field not in obj:
        return None, 404

    # access token grant access
    if model == "ir.attachment" and access_token:
        obj = obj.sudo()
        if not consteq(obj.access_token or u"", access_token):
            return None, 403

    # check read access
    try:
        last_update = obj["__last_update"]  # noqa: F841
    except AccessError:
        return None, 403

    return obj, 200


class BinaryExtended(Binary):
    @route()
    def content_image(self, **kw):
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

        if not (width or height):
            # image is definately won't be resized
            _logger.debug("Image not gonna be be resized")
            return super(BinaryExtended, self).content_image(**kw)

        record, status = _get_record_and_check(
            env, xmlid, model, id, field, access_token
        )
        if not record:
            return super(BinaryExtended, self).content_image(**kw)

        if not record._fields[field].attachment:
            _logger.debug(
                "Field {} on model {} is not stored as attachment".format(field, model)
            )
            return super(BinaryExtended, self).content_image(**kw)

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
                return super(BinaryExtended, self).content_image(**kw)
            attachment.ensure_one()
        resized = attachment.get_resized_from_cache(width, height, crop)

        if resized:
            _logger.debug("Cache hit!")
            kw["id"] = resized.resized_attachment_id.id
            kw["model"] = "ir.attachment"
            kw["field"] = "datas"
            kw["width"] = kw["height"] = 0
            kw["crop"] = 0
            return super(BinaryExtended, self).content_image(**kw)

        # storing resized image from response to cache
        response = super(BinaryExtended, self).content_image(**kw)
        if response.status_code != 200:
            _logger.debug("Cache miss and not 200 status")
            return response

        _logger.debug("Cache miss and storing")
        content = b"".join(response.response)
        attachment.store_resized_to_cache(
            base64.b64encode(content), width, height, crop
        )
        return response
