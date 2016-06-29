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
        author_name = http.request.env.user.name # current user name
        author_id = http.request.env.user.id # current user ID
        task_id = 13 # current Task

        task = request.env["project.task"].search([('user_id', '=', author_id)]) # all tasks current user
        work = request.env["project.task.work"].search([('user_id', '=', author_id), ('task_id', '=', task_id)]) # all works in tasks current user and current task
        stopline = request.env["project.task"].search([('id', '=', task_id)]) # stopline in current task

        # как определить текущую задачу? пусть временно текущая задача id = 13
        # надо получить конечное значение для таймера (значение времени, сколько нужно работать)
        # данный результат отправить в js не нужно по умолчанию 2 часа.

        notification = []


        print("--------------------------------------")
        print(task)
        print(work)
        print("stopline")
        print(stopline.datetime_stopline)
        print("--------------------------------------")

        if stopline.datetime_stopline is not False:
            notification.append({'stopline': stopline.datetime_stopline})

        notification.append({'author_name': author_name, 'author_id': author_id, 'task_id': task_id})

        return notification