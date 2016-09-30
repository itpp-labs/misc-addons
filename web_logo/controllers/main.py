# -*- coding: utf-8 -*-
import openerp
from openerp import http
from openerp.addons.web.controllers.main import Binary
import functools
from openerp.http import request
from openerp.modules import get_module_resource
from cStringIO import StringIO
db_monodb = http.db_monodb


class BinaryCustom(Binary):

    @http.route([
        '/web/binary/company_logo',
        '/logo',
        '/logo.png',
    ], type='http', auth="none")
    def company_logo(self, dbname=None, company_id=None, **kw):
        imgname = 'logo.png'
        placeholder = functools.partial(get_module_resource, 'web', 'static', 'src', 'img')
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
                    if company_id:
                        cr.execute("""SELECT c.logo_web, c.write_date
                                        FROM res_company c
                                       WHERE c.id = %s
                               """, (company_id,))
                    else:
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
