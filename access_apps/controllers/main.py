from openerp import http
from openerp.http import request
from openerp.addons.web_settings_dashboard.controllers.main import WebSettingsDashboard
from openerp import SUPERUSER_ID


class WebSettingsDashboardCustom(WebSettingsDashboard):
    @http.route('/web_settings_dashboard/data', type='json', auth='user')
    def web_settings_dashboard_data(self, **kw):
        has_access_to_apps = request.registry['res.users'].has_group(request.cr, request.uid, 'access_apps.group_show_modules_menu')
        # issue: due to unknown reason has_group is always invoked with superuser as uid param in new API
        # has_access_to_apps = request.env.user.has_group('access_apps.group_show_modules_menu')
        request.env = request.env(user=SUPERUSER_ID)
        res = super(WebSettingsDashboardCustom, self).web_settings_dashboard_data(**kw)
        res['has_access_to_apps'] = has_access_to_apps
        return res
