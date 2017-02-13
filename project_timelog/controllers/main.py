# -*- coding: utf-8 -*-
import datetime
from openerp import http
from openerp.http import request


class TimelogController(http.Controller):

    @http.route('/timelog/init', type="json", auth="public")
    def init_timelog(self, **kwargs):
        timelog_obj = request.env["project.timelog"]
        all_timelog_current_user = timelog_obj.search_count([("user_id", "=", http.request.env.user.id)])

        all_timelog_current_user_in_current_task = timelog_obj.search([("user_id", "=", http.request.env.user.id), ("work_id.task_id", "=", http.request.env.user.active_task_id.id)])

        # stopline for current task
        stopline = http.request.env.user.active_task_id

        # All logs for other users and current task
        all_timelog_other_users = timelog_obj.search([("user_id", "!=", http.request.env.user.id), ("work_id.task_id", "=", http.request.env.user.active_task_id.id)])

        timelog = http.request.env.user.active_work_id.timelog_ids

        last_timelog = 0
        if timelog:
            last_timelog = timelog[-1].id

        subtask = http.request.env.user.active_work_id
        task = http.request.env.user.active_task_id

        subtask_name = "None"
        if subtask:
            subtask_name = subtask.name

        task_name = "None"
        if task:
            task_name = task.name

        # 1. All time (today) in current work for current user
        log_timer = 0
        if all_timelog_current_user:
            if timelog and timelog[0].start_datetime is not False:
                date_object = datetime.datetime.strptime(timelog[0].start_datetime, "%Y-%m-%d %H:%M:%S")
                if date_object.day == datetime.datetime.now().day:
                    log_timer = int(round(http.request.env.user.active_work_id.hours * 3600, 0))

        play_status = False
        if all_timelog_current_user:
            if timelog and timelog[-1].end_datetime is False:
                play_status = True
                start_datetime = datetime.datetime.strptime(timelog[-1].start_datetime, "%Y-%m-%d %H:%M:%S")
                end_datetime = datetime.datetime.now()
                play_status_time = (end_datetime - start_datetime).total_seconds()
                log_timer = int(round(play_status_time, 0)) + log_timer

        # 2. All time in current task for current user
        task_timer = 0
        if all_timelog_current_user_in_current_task:
            # all work for current user in active task
            all_work = request.env["project.task.work"].search([('task_id', '=', http.request.env.user.active_task_id.id), ('user_id', '=', http.request.env.user.id)])
            sum_spent = 0
            for r in all_work:
                sum_spent = sum_spent + r.hours
            task_timer = int(round(sum_spent * 3600, 0))
            if play_status:
                task_timer = task_timer + play_status_time

        # 3. All the time for today 3.
        day_timer = 0
        timelog_today = timelog_obj.search([("user_id", "=", http.request.env.user.id), ("start_datetime", ">=", datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')), ("start_datetime", "<=", datetime.datetime.now().strftime('%Y-%m-%d 23:59:59'))])
        if timelog_today:
            today_work_id = []
            for r in timelog_today:
                today_work_id.append(r.work_id.id)
            today_work_id = list(set(today_work_id))
            sum_spent_day = 0
            for e in today_work_id:
                sum_spent_day = sum_spent_day + request.env["project.task.work"].search([("id", "=", e)]).hours
            day_timer = int(round(sum_spent_day * 3600, 0))
            if play_status:
                day_timer = day_timer + play_status_time

        # 4. All time this week
        week_timer = 0
        today = datetime.datetime.today()
        monday = today - datetime.timedelta(datetime.datetime.weekday(today))
        sunday = today + datetime.timedelta(6 - datetime.datetime.weekday(today))
        timelog_this_week = timelog_obj.search([("user_id", "=", http.request.env.user.id), ("start_datetime", ">=", monday.strftime('%Y-%m-%d 00:00:00')), ("start_datetime", "<=", sunday.strftime('%Y-%m-%d 23:59:59'))])
        if timelog_this_week:
            week_work_id = []
            for r in timelog_this_week:
                week_work_id.append(r.work_id.id)
            week_work_id = list(set(week_work_id))
            sum_spent_week = 0
            for e in week_work_id:
                sum_spent_week = sum_spent_week + request.env["project.task.work"].search([("id", "=", e)]).hours
            week_timer = int(round(sum_spent_week * 3600, 0))
            if play_status:
                week_timer = week_timer + play_status_time

        second_timer_info = []
        desctiption_timer = ''
        if all_timelog_other_users:
            another_users = []
            for e in all_timelog_other_users:
                another_users.append(str(e.user_id.name))
            another_users = list(set(another_users))
            for e in another_users:
                res = timelog_obj.search([("user_id.name", "=", e), ("work_id.task_id", "=", http.request.env.user.active_task_id.id)])
                sum_another_timelog = 0
                for i in res:
                    sum_another_timelog = sum_another_timelog + i.corrected_duration
                sum_another_timelog = 3600 * sum_another_timelog
                sum_another_timelog = datetime.timedelta(seconds=round(sum_another_timelog, 0))
                second_timer_info.append(e + ": " + str(sum_another_timelog) + "\n")

            for e in second_timer_info:
                desctiption_timer = desctiption_timer + e

        config = request.env["ir.config_parameter"]
        convert_sec = 3600

        if task.datetime_stopline is False:
            timerstopline = False
        else:
            stopline_date = datetime.datetime.strptime(task.datetime_stopline, "%Y-%m-%d %H:%M:%S")
            if stopline_date <= datetime.datetime.today():
                timerstopline = True
            else:
                timerstopline = False

        time_subtasks = int(round(float(config.get_param("project_timelog.time_subtasks"))*convert_sec, 0))

        task_id = http.request.env.user.active_task_id.id
        if task_id is False:
            task_id = 0
        work_id = http.request.env.user.active_work_id.id
        if work_id is False:
            work_id = 0

        end_datetime_status = True
        t = http.request.env.user.active_work_id.timelog_ids
        if t and t[-1].end_datetime is False:
            end_datetime_status = False

        resultat = {
            'timer_status': play_status,
            'task_id': task_id,
            'work_id': work_id,
            "planned_hours": int(round(stopline.planned_hours*convert_sec, 0)),
            "stopline": timerstopline,

            "init_log_timer": log_timer,
            "init_task_timer": task_timer,
            "init_day_timer": day_timer,
            "init_week_timer": week_timer,

            "time_subtasks": time_subtasks,
            "time_warning_subtasks": time_subtasks - int(round(float(config.get_param("project_timelog.time_warning_subtasks"))*convert_sec, 0)),

            "normal_time_day": int(round(float(config.get_param("project_timelog.normal_time_day"))*convert_sec, 0)),
            "good_time_day": int(round(float(config.get_param("project_timelog.good_time_day"))*convert_sec, 0)),

            "normal_time_week": int(round(float(config.get_param("project_timelog.normal_time_week"))*convert_sec, 0)),
            "good_time_week": int(round(float(config.get_param("project_timelog.good_time_week"))*convert_sec, 0)),

            "subtask_name": subtask_name,
            "description_second_timer": desctiption_timer,
            "task_name": task_name,

            "timelog_id": last_timelog,
            "end_datetime_status": end_datetime_status
        }
        return resultat

    @http.route('/timelog/connection', type='http', auth="public")
    def connection(self, **kwargs):
        return "1"

    @http.route('/timelog/upd', type="json", auth="public")
    def get_server_data(self, **kwargs):
        return {
            "uid": http.request.env.user.id,
            "dbname": http.request.cr.dbname,
        }
