# -*- coding: utf-8 -*-
import datetime
from openerp import http
from openerp.http import request


class TimelogController(http.Controller):

    @http.route('/timelog/init', type="json", auth="public")
    def init_timelog(self, **kwargs):
        timelog_obj = request.env["project.timelog"]
        # get current user
        user = http.request.env.user

        # get current task and work of current user
        subtask = user.active_work_id
        task = user.active_task_id

        # get the timelogs of current user
        user_timelogs = timelog_obj.search_count([("user_id", "=", user.id)])

        # get the timelogs of current user for current task
        # task_user_timelogs = user_timelogs.filter(lambda x: x.work_id.task_id == task.id)
        task_user_timelogs = timelog_obj.search([("user_id", "=", user.id), ("work_id.task_id", "=", task.id)])

        # get timelogs of other users in current task
        timelogs_other_users = timelog_obj.search([("user_id", "!=", user.id), ("work_id.task_id", "=", task.id)])

        # get all timelogs of current work
        timelogs = subtask.timelog_ids

        # get last records
        last_timelog = timelogs[-1].id if timelogs else False
        subtask_name = subtask.name if subtask else False
        task_name = task.name if task else False

        # 1. get common time of current work (current day)
        log_timer = 0
        if timelogs and timelogs[0].start_datetime is not False:
            date_object = datetime.datetime.strptime(timelogs[0].start_datetime, "%Y-%m-%d %H:%M:%S")
            if date_object.day == datetime.datetime.now().day:
                log_timer = int(round(subtask.unit_amount * 3600, 0))

        timer_status = False
        if timelogs and timelogs[-1].end_datetime is False:
            timer_status = True
            start_datetime = datetime.datetime.strptime(timelogs[-1].start_datetime, "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.datetime.now()
            current_time = (end_datetime - start_datetime).total_seconds()
            log_timer = int(round(current_time, 0)) + log_timer

        # 2. All time in current task for current user
        task_timer = 0
        if task_user_timelogs:
            # all work for current user in active task
            all_work = request.env["account.analytic.line"].search([('task_id', '=', task.id), ('user_id', '=', user.id)])
            sum_spent = 0
            for r in all_work:
                sum_spent = sum_spent + r.unit_amount
            task_timer = int(round(sum_spent * 3600, 0))
            if timer_status:
                task_timer = task_timer + current_time

        # 3. All the time for today 3.
        day_timer = 0
        timelog_today = timelog_obj.search([("user_id", "=", user.id), ("start_datetime", ">=", datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')), ("start_datetime", "<=", datetime.datetime.now().strftime('%Y-%m-%d 23:59:59'))])
        if timelog_today:
            work_ids = []
            for r in timelog_today:
                work_ids.append(r.work_id.id)
            # get unique work_ids of current day
            work_ids = list(set(work_ids))
            sum_spent_day = 0
            for e in work_ids:
                sum_spent_day = sum_spent_day + request.env["account.analytic.line"].search([("id", "=", e)]).unit_amount
            day_timer = int(round(sum_spent_day * 3600, 0))
            if timer_status:
                day_timer = day_timer + current_time

        # 4. All time this week
        week_timer = 0
        today = datetime.datetime.today()
        monday = today - datetime.timedelta(datetime.datetime.weekday(today))
        sunday = today + datetime.timedelta(6 - datetime.datetime.weekday(today))
        timelog_this_week = timelog_obj.search([("user_id", "=", user.id), ("start_datetime", ">=", monday.strftime('%Y-%m-%d 00:00:00')), ("start_datetime", "<=", sunday.strftime('%Y-%m-%d 23:59:59'))])
        if timelog_this_week:
            week_work_ids = []
            for r in timelog_this_week:
                week_work_ids.append(r.work_id.id)
            # get unique work_ids of current week
            week_work_ids = list(set(week_work_ids))
            sum_spent_week = 0
            for e in week_work_ids:
                sum_spent_week = sum_spent_week + request.env["account.analytic.line"].search([("id", "=", e)]).unit_amount
            week_timer = int(round(sum_spent_week * 3600, 0))
            if timer_status:
                week_timer = week_timer + current_time

        # get data about timers
        second_timer_info = []
        desctiption_timer = ''

        if timelogs_other_users:
            another_users = []
            for u in timelogs_other_users:
                another_users.append({
                    'id': u.user_id.id,
                    'name': u.user_id.name
                })
            another_users = list(set(another_users))
            for u in another_users:
                res = timelog_obj.search([("user_id", "=", u['id']), ("work_id.task_id", "=", task.id)])
                sum_another_timelog = 0
                for i in res:
                    sum_another_timelog = sum_another_timelog + i.corrected_duration
                sum_another_timelog = 3600 * sum_another_timelog
                sum_another_timelog = datetime.timedelta(seconds=round(sum_another_timelog, 0))
                second_timer_info.append(u['name'] + ": " + str(sum_another_timelog) + "\n")

            for r in second_timer_info:
                desctiption_timer = desctiption_timer + r

        config = request.env["ir.config_parameter"]
        convert_sec = 3600

        timer_stopline = False
        if task.datetime_stopline:
            stopline_date = datetime.datetime.strptime(task.datetime_stopline, "%Y-%m-%d %H:%M:%S")
            if stopline_date <= datetime.datetime.today():
                timer_stopline = True

        # get configs for timer
        time_subtasks = int(round(float(config.get_param("project_timelog.time_subtasks"))*convert_sec, 0))
        time_warning_subtasks = time_subtasks - int(
            round(float(config.get_param("project_timelog.time_warning_subtasks")) * convert_sec, 0))
        normal_time_day = int(round(float(config.get_param("project_timelog.normal_time_day")) * convert_sec, 0))
        good_time_day = int(round(float(config.get_param("project_timelog.good_time_day")) * convert_sec, 0))
        normal_time_week = int(round(float(config.get_param("project_timelog.normal_time_week")) * convert_sec, 0))
        good_time_week = int(round(float(config.get_param("project_timelog.good_time_week")) * convert_sec, 0))

        end_datetime_status = True
        if timelogs and timelogs[-1].end_datetime is False:
            end_datetime_status = False

        return {
            'timer_status': timer_status,
            'task_id': task.id or False,
            'work_id': subtask.id or False,
            "planned_hours": int(round(task.planned_hours*convert_sec, 0)),
            "stopline": timer_stopline,

            "init_log_timer": int(log_timer),
            "init_task_timer": int(task_timer),
            "init_day_timer": int(day_timer),
            "init_week_timer": int(week_timer),

            "time_subtasks": time_subtasks,
            "time_warning_subtasks": time_warning_subtasks,

            "normal_time_day": normal_time_day,
            "good_time_day": good_time_day,

            "normal_time_week": normal_time_week,
            "good_time_week": good_time_week,

            "subtask_name": subtask_name,
            "description_second_timer": desctiption_timer,
            "task_name": task_name,

            "timelog_id": last_timelog,
            "end_datetime_status": end_datetime_status
        }

    @http.route('/timelog/connection', type='http', auth="public")
    def connection(self, **kwargs):
        return True
