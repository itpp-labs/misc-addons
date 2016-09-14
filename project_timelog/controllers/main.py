# -*- coding: utf-8 -*-
import datetime
import openerp
from openerp import http
from openerp.http import request


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

        # stopline for current task
        stopline = request.env["project.task"].search([('id', '=', current_user_active_task_id)])

        # All logs
        all_timelog = request.env["project.timelog"]

        # All logs for current user
        all_timelog_current_user = all_timelog.search([("user_id", "=", current_user.id)])

        # All logs for current user and current task
        all_timelog_current_user_and_task = all_timelog.search([("user_id", "=", current_user.id), ("work_id.task_id", "=", current_user_active_task_id)])

        # All logs for other users and current task
        all_timelog_other_users = all_timelog.search([("user_id", "!=", current_user.id), ("work_id.task_id", "=", current_user_active_task_id)])

        first_timelog = all_timelog.search([("work_id", "=", current_user_active_work_id)])

        last_timelog = 0

        if len(first_timelog) > 1:
            last_timelog = first_timelog[-1].id
        elif len(first_timelog) == 1:
            last_timelog = first_timelog[0].id

        subwork = request.env["project.task.work"].search([("id", "=", current_user_active_work_id)])  # current user

        subwork_name = "None"
        if len(subwork) is not 0:
            subwork_name = subwork.name

        # 1. All time (today) in current work for current user
        first_init_time = 0
        if len(all_timelog_current_user) is not 0:
            if len(first_timelog) > 0 and first_timelog[0].start_datetime is not False:
                date_object = datetime.datetime.strptime(first_timelog[0].start_datetime, "%Y-%m-%d %H:%M:%S")
                if date_object.day == datetime.datetime.now().day:
                    first_init_time = request.env["project.timelog"].sum_time(first_timelog)

        play_status = False
        if len(all_timelog_current_user) is not 0:
            if first_timelog[-1].end_datetime is False:
                play_status = True

        # 2. All time in current task for current user
        second_init_time = 0
        if len(all_timelog_current_user_and_task) is not 0:
            second_init_time = request.env["project.timelog"].sum_time(all_timelog_current_user_and_task)

        # 3. All the time for today 3.
        third_init_time = 0
        timelog_today = all_timelog.search([("user_id", "=", current_user.id), ("start_datetime", ">=", datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')), ("start_datetime", "<=", datetime.datetime.now().strftime('%Y-%m-%d 23:59:59'))])
        if len(timelog_today) is not 0:
            third_init_time = request.env["project.timelog"].sum_time(timelog_today)

        # 4. All time this week
        fourth_init_time = 0
        today = datetime.datetime.today()
        monday = today - datetime.timedelta(datetime.datetime.weekday(today))
        sunday = today + datetime.timedelta(6 - datetime.datetime.weekday(today))
        timelog_this_week = all_timelog.search([("user_id", "=", current_user.id), ("start_datetime", ">=", monday.strftime('%Y-%m-%d 00:00:00')), ("start_datetime", "<=", sunday.strftime('%Y-%m-%d 23:59:59'))])
        if len(timelog_this_week) is not 0:
            fourth_init_time = request.env["project.timelog"].sum_time(timelog_this_week)

        second_timer_info = []
        desctiption_timer = ''
        if len(all_timelog_other_users) != 0:
            all_timelog_other_users = all_timelog.search([("user_id", "!=", current_user.id), ("work_id.task_id", "=", current_user_active_task_id)])
            another_users = []
            for e in all_timelog_other_users:
                another_users.append(str(e.user_id.name))
            another_users = list(set(another_users))
            for e in another_users:
                res = all_timelog.search([("user_id.name", "=", e), ("work_id.task_id", "=", current_user_active_task_id)])
                sum_another_timelog = 0
                for i in res:
                    sum_another_timelog = sum_another_timelog + i.duration
                sum_another_timelog = 3600 * sum_another_timelog
                sum_another_timelog = datetime.timedelta(seconds=round(sum_another_timelog, 0))
                second_timer_info.append(e + ": " + str(sum_another_timelog))

            for e in second_timer_info:
                desctiption_timer = desctiption_timer + e

        config = request.env["ir.config_parameter"]
        convert_sec = 3600

        timerstopline = False
        time_subtasks = int(round(float(config.get_param("project_timelog.time_subtasks"))*convert_sec, 0))

        resultat = {
            'timer_status': play_status,
            'task_id': current_user_active_task_id,
            'work_id': current_user_active_work_id,
            "planned_hours": int(round(stopline.planned_hours*convert_sec, 0)),
            "stopline": timerstopline,

            "init_first_timer": first_init_time,
            "init_second_timer": second_init_time,
            "init_third_timer": third_init_time,
            "init_fourth_timer": fourth_init_time,

            "time_subtasks": time_subtasks,
            "time_warning_subtasks": time_subtasks - int(round(float(config.get_param("project_timelog.time_warning_subtasks"))*convert_sec, 0)),

            "normal_time_day": int(round(float(config.get_param("project_timelog.normal_time_day"))*convert_sec, 0)),
            "good_time_day": int(round(float(config.get_param("project_timelog.good_time_day"))*convert_sec, 0)),

            "normal_time_week": int(round(float(config.get_param("project_timelog.normal_time_week"))*convert_sec, 0)),
            "good_time_week": int(round(float(config.get_param("project_timelog.good_time_week"))*convert_sec, 0)),

            "name_first_timer": subwork_name,
            "description_second_timer": desctiption_timer,

            "timelog_id": last_timelog
        }

        return resultat

    @http.route('/timelog/connection', type='http', auth="public")
    def connection(self, **kwargs):
        return "1"
