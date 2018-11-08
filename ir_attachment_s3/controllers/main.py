# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging
import werkzeug

import odoo
from odoo.http import request, route
from odoo.addons.web.controllers.main import Binary
# TODO some code can be part of ir_attachment_url

_logger = logging.getLogger(__name__)


class BinaryExtended(Binary):

    def redirect_to_url(self, url):
        return werkzeug.utils.redirect(url, code=301)

    @route()
    def content_image(self, xmlid=None, model='ir.attachment', id=None, field='datas', filename_field='datas_fname', unique=None, filename=None, mimetype=None, download=None, width=0, height=0):

        res = super(BinaryExtended, self).content_image(xmlid, model, id, field, filename_field, unique, filename, mimetype, download, width, height)

        if not (res.status_code == 301 and (width or height)):
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
        else:
            attachment = env['ir.http'].find_field_attachment(env, model, field, obj)

        if not attachment:
            # imposible case?
            _logger.error('Attachment is not found')
            return res

        # FIX SIZES
        height = int(height or 0)
        width = int(width or 0)
        # resize maximum 500*500
        if width > 500:
            width = 500
        if height > 500:
            height = 500

        # CHECK FOR CACHE.
        # We may already uploaded that resized image
        cache = env['ir.attachment.resized'].sudo().search([
            ('attachment_id', '=', attachment.id),
            ('width', '=', width),
            ('height', '=', height),
        ])
        if cache:
            url = cache.resized_attachment_id.url
            return self.redirect_to_url(url)

        # PREPARE CACHE
        content = attachment.datas
        content = odoo.tools.image_resize_image(base64_source=content, size=(width or None, height or None), encoding='base64', filetype='PNG')
        resized_attachment = env['ir.attachment'].with_context(force_s3=True).create({
            'name': '%sx%s %s' % (width, height, attachment.name),
            'datas': content,
        })

        env['ir.attachment.resized'].sudo().create({
            'attachment_id': attachment.id,
            'width': width,
            'height': height,
            'resized_attachment_id': resized_attachment.id,
        })

        url = resized_attachment.url
        return self.redirect_to_url(url)
