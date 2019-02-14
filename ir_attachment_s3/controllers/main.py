# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo.http import request, route
from odoo.addons.ir_attachment_url.controllers.main import SIZES_MAP, BinaryExtended as Binary

_logger = logging.getLogger(__name__)


class BinaryExtended(Binary):

    @route()
    def content_image(self, xmlid=None, model='ir.attachment', id=None, field='datas', filename_field='datas_fname', unique=None, filename=None, mimetype=None, download=None, width=0, height=0):

        res = super(BinaryExtended, self).content_image(xmlid, model, id, field, filename_field, unique, filename, mimetype, download, width, height)

        is_product_product_image = model == 'product.product' and field in ('image', 'image_small', 'image_medium')
        if not (res.status_code == 301 and (width or height)) and not is_product_product_image:
            return res

        # * check that it's image on s3
        # * upload resized image if needed
        # * return url to resized image

        # FIND ATTACHMENT. The code is copy-pasted from binary_content method
        env = request.env
        # get object and content
        obj = None
        if xmlid:
            obj = env.ref(xmlid, False)
        elif id and model in env.registry:
            obj = env[model].browse(int(id))

        attachment = None
        if model == 'ir.attachment':
            attachment = obj
        elif is_product_product_image:
            attachment = env['ir.http']._find_field_attachment(env, model, field, obj.id)
            if not attachment:
                image_variant_attachment = env['ir.http']._find_field_attachment(env, model, 'image_variant', obj.id)
                if image_variant_attachment:
                    w, h = SIZES_MAP[field]
                    resized_attachment = \
                        image_variant_attachment._get_resized_from_cache(w, h) or \
                        image_variant_attachment._set_resized_to_cache(w, h, field=field)
                    attachment = resized_attachment.resized_attachment_id

        if not attachment and model != 'ir.attachment':
            attachment = env['ir.http'].find_field_attachment(env, model, field, obj)

        if not attachment:
            # imposible case?
            _logger.error('Attachment is not found')
            return res

        # if not need to resize
        if not (width and height):
            url = attachment.url
            return self.redirect_to_url(url)

        # FIX SIZES
        height = int(height or 0)
        width = int(width or 0)
        # resize maximum 500*500
        if width > 500:
            width = 500
        if height > 500:
            height = 500

        resized_attachment = \
            attachment._get_resized_from_cache(width, height) or \
            attachment._set_resized_to_cache(width, height)
        url = resized_attachment.resized_attachment_id.url
        return self.redirect_to_url(url)
