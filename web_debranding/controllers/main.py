import openerp
from openerp import http, SUPERUSER_ID
from openerp.addons.web.controllers.main import Binary
from openerp.addons.web_settings_dashboard.controllers.main import WebSettingsDashboard
import functools
from openerp.http import request, serialize_exception as _serialize_exception
from openerp.modules import get_module_resource
from cStringIO import StringIO
db_monodb = http.db_monodb


class WebSettingsDashboardCustom(WebSettingsDashboard):
    @http.route('/web_settings_dashboard/data', type='json', auth='user')
    def web_settings_dashboard_data(self, **kw):
        active_users = request.env['res.users'].search_count([('active', '=', True), ('log_ids', '!=', False)])
        pending_users = request.env['res.users'].search([('log_ids', '=', False)], order="create_date desc")

        return {
            'users_info': {
                'active_users': active_users,
                'pending_users': zip(pending_users.mapped('id'), pending_users.mapped('login')),
                'user_form_view_id': request.env['ir.model.data'].xmlid_to_res_id("base.view_users_form"),
            },
        }


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
