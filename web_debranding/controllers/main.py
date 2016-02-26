# -*- coding: utf-8 -*-

import openerp
from openerp import http, SUPERUSER_ID
from openerp.addons.web.controllers.main import Binary
from openerp.addons.web.controllers.main import WebClient
from openerp.addons.web.controllers import main as controllers_main
import functools
from openerp.http import request, serialize_exception as _serialize_exception
from openerp.modules import get_module_resource
from cStringIO import StringIO
db_monodb = http.db_monodb
import re


class BinaryCustom(Binary):
    @http.route([
        '/web/binary/company_logo',
        '/logo',
        '/logo.png',
    ], type='http', auth="none")
    def company_logo(self, dbname=None, **kw):
        imgname = 'logo.png'
        default_logo_module = 'web_debranding'
        if request.session.db:
            request.env['ir.config_parameter'].get_param('web_debranding.default_logo_module')
        placeholder = functools.partial(get_module_resource, default_logo_module, 'static', 'src', 'img')
        uid = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = db_monodb()

        if not uid:
            uid = openerp.SUPERUSER_ID

        if not dbname:
            response = http.send_file(placeholder(imgname))
        else:
            try:
                # create an empty registry
                registry = openerp.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    cr.execute("""SELECT c.logo_web, c.write_date
                                    FROM res_users u
                               LEFT JOIN res_company c
                                      ON c.id = u.company_id
                                   WHERE u.id = %s
                               """, (uid,))
                    row = cr.fetchone()
                    if row and row[0]:
                        image_data = StringIO(str(row[0]).decode('base64'))
                        response = http.send_file(image_data, filename=imgname, mtime=row[1])
                    else:
                        response = http.send_file(placeholder('nologo.png'))
            except Exception:
                response = http.send_file(placeholder(imgname))

        return response


class WebClientCustom(WebClient):

    @http.route('/web/webclient/qweb', type='http', auth="none")
    def qweb(self, mods=None, db=None):
        files = [f[0] for f in controllers_main.manifest_glob('qweb', addons=mods, db=db)]
        last_modified = controllers_main.get_last_modified(files)
        if request.httprequest.if_modified_since and request.httprequest.if_modified_since >= last_modified:
            return controllers_main.werkzeug.wrappers.Response(status=304)

        content, checksum = controllers_main.concat_xml(files)
        if request.context['lang'] == 'en_US':
            content = content.decode('utf-8')
            content = self._debrand(content)

        return controllers_main.make_conditional(
            request.make_response(content, [('Content-Type', 'text/xml')]),
            last_modified, checksum)

    @http.route('/web/webclient/translations', type='json', auth="none")
    def translations(self, mods=None, lang=None):
        res = super(WebClientCustom, self).translations(mods, lang)
        for module_key, module_vals in res['modules'].iteritems():
            for message in module_vals['messages']:
                message['id'] = self._debrand(message['id'])
                message['string'] = self._debrand(message['string'])
        return res

    def _debrand(self, string):
        new_company = request.env['ir.config_parameter'].get_param('web_debranding.new_name')
        return re.sub(r'[Oo]doo', new_company, string)
