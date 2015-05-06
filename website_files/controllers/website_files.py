# -*- coding: utf-8 -*-
import re
import json
import openerp
from openerp import http
from openerp.http import request
import logging
_logger = logging.getLogger(__name__)


class WebsiteFile(openerp.addons.website.controllers.main.Website):
    def _find_website_filename(self, filename):
        name = ext = ''
        res = re.match('(.*)(\.[^.]+)', filename)
        if res:
            name = res.group(1)
            ext = res.group(2)
        else:
            name = filename

        pattern = '%s-[0-9]+%s' % (name, ext)

        request.cr.execute("""
        SELECT count(*)
        FROM ir_attachment
        WHERE datas_fname SIMILAR TO %s
        """, (pattern,))

        count = request.cr.fetchone()[0]

        return '%s-%s%s' % (name, count+1, ext)

    @http.route('/website/attach_file', type='http', auth='user',
                methods=['POST'], website=True)
    def attach_file(self, func, upload=None, overwrite=False):
        filename = website_file_url = message = None
        try:
            file_data = upload.read().encode('base64')
            filename = upload.filename or 'undefined'
            attachment = request.env['ir.attachment'].search([
                ('website_file', '=', True),
                ('datas_fname', '=', filename)])
            if attachment:
                attachment = attachment[0]
                if overwrite:
                    print 'overwrite attachment',
                    attachment.datas = file_data
                else:
                    filename = self._find_website_filename(filename)
                    print 'new filename', filename
                    attachment = None

            if not attachment:
                attachment = request.env['ir.attachment'].create({
                    'name': filename,
                    'datas': file_data,
                    'datas_fname': filename,
                    'website_file': True,
                })
                print 'create attachment', attachment.id, filename

            website_file_url = attachment.website_file_url
        except Exception, e:
            _logger.exception("Failed to upload file to attachment")
            message = unicode(e)

        return """<script type='text/javascript'>
            window.parent['%s'](%s, %s, %s);
        </script>""" % (func,
                        json.dumps(filename),
                        json.dumps(website_file_url),
                        json.dumps(message))
