# -*- coding: utf-8 -*-
import openerp
from openerp import http
from openerp.http import request
from openerp.addons.base import res
import werkzeug

class Controller(openerp.addons.bus.bus.Controller):
    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            registry, cr, uid, context = request.registry, request.cr, request.session.uid, request.context
            channels.append((request.db, 'project.timelog', request.uid))
        return super(Controller, self)._poll(dbname, channels, last, options)

    @http.route('/timelog/init', type="json", auth="public")
    def init_timelog(self, **kwargs):
        current_user = request.env["res.users"].search([("id", "=", http.request.env.user.id)])
        current_user_active_task_id = current_user.active_task_id
        current_user_active_work_id = current_user.active_work_id

        stopline = request.env["project.task"].search([('id', '=', current_user_active_task_id)]) # stopline for current task

        # Время по текущей подзадаче
        # Общее время по текущей задачи (суммируется только данные текущего пользователя)
        # Общее время за сегодняшний день.
        # Общее время за текущую неделю.

        notification = []

        if stopline.datetime_stopline is not False:
            notification.append({'stopline': stopline.datetime_stopline})

        notification.append({'task_id': current_user_active_task_id, 'work_id': current_user_active_work_id})

        return notification