# -*- coding: utf-8 -*-
import datetime
import time
from openerp import models, fields, api, SUPERUSER_ID
from openerp import http

class ProjectTimeLog(models.Model):
    _name = "project.timelog"
    _description = "project timelog"

    work_id = fields.Many2one("project.task.work", "Task", required=True)
    task_name = fields.Char(related='work_id.task_id.name', store=True)
    project_name = fields.Char(related='work_id.task_id.project_id.name', store=True)
    start_datetime = fields.Datetime(string="Start date", default=datetime.datetime.now())
    end_datetime = fields.Datetime(string="End date")
    duration = fields.Float(string="Duration", compute="_compute_duration", store=True)
    user_id = fields.Many2one("res.users", string="User name")

    @api.multi
    def sum_time(self, timelog):
        sum_time = datetime.timedelta(0)
        if timelog[-1].end_datetime is False:
            time_now = datetime.datetime.now()
            sum_time = sum_time + (time_now - datetime.datetime.strptime(timelog[-1].start_datetime, "%Y-%m-%d %H:%M:%S"))
            timelog = timelog[:-1]
        for e in timelog:
            date_start_object = datetime.datetime.strptime(e.start_datetime, "%Y-%m-%d %H:%M:%S")
            date_end_object = datetime.datetime.strptime(e.end_datetime, "%Y-%m-%d %H:%M:%S")
            sum_time = sum_time + (date_end_object-date_start_object)
        return int(round(sum_time.total_seconds(),0))

    @api.one
    @api.depends("start_datetime", "end_datetime")
    def _compute_duration(self):
        if self.end_datetime is False:
            self.duration = False
        else:
            if type(self.start_datetime) is str:
                start_datetime  = datetime.datetime.strptime(self.start_datetime, "%Y-%m-%d %H:%M:%S")
            else:
                start_datetime  = self.start_datetime

            if type(self.end_datetime) is str:
                end_datetime = datetime.datetime.strptime(self.end_datetime, "%Y-%m-%d %H:%M:%S")
            else:
                end_datetime = self.end_datetime

            resultat = end_datetime - start_datetime
            self.duration = int(round(resultat.total_seconds(),0))/3600.0

class task(models.Model):
    _inherit = ["project.task"]
    datetime_stopline = fields.Datetime(string="Stopline", select=True, copy=False)

class Users(models.Model):
    _inherit = ["res.users"]

    active_work_id = fields.Integer(default=0)
    active_task_id = fields.Integer(default=0)

class project_work(models.Model):
    _inherit = ["project.task.work"]

    timelog_ids = fields.One2many("project.timelog", "work_id", "Timelog")

    @api.multi
    def play_timer(self):
        if self.env.user.id != self.user_id.id:
            # current user is not match user with solved task
            return False

        duration = self.env["project.timelog"].search([("work_id", "=", self.id), ("user_id", "=", self.env.user.id)])
        config = self.env["ir.config_parameter"].get_param("project_timelog.time_subtasks")

        sum_timelog = 0.0
        if len(duration)>0 and len(config)>0:
            for e in duration:
                sum_timelog = sum_timelog + round(e.duration,3)
            if sum_timelog >= round(float(config),3):
                return False

        current_user = self.env["res.users"].search([("id", "=", self.user_id.id)])
        current_date = datetime.datetime.now()

        first_timelog = self.env["project.timelog"].search([("work_id", "=", self.id)])

        if len(first_timelog)>0 and first_timelog[0].end_datetime is not False:
            date_object = datetime.datetime.strptime(first_timelog[0].end_datetime, "%Y-%m-%d %H:%M:%S")
            if date_object is not False and date_object.day != current_date.day:
                # there are timelogs yesterday
                return False

        # необходимо сделать проверку, если подзадача уже работала больше 5 минут и мы переключились на новую
        # и затем решили перейти на предыдущую, сделать ее не активной, для этого надо добавить новое после "статус"
        # которое будет вычисляться и будет иметься несколько статусов "неактивная, новый, остановленный, текущий"

        # record data for current user (last active timer)
        current_user.write({
            "active_work_id": self.id,
            "active_task_id": self.task_id.id,
        })

        # create new timelog for current work
        last_timelog = self.env['project.timelog'].create({
            "work_id": self.id,
            "user_id": self.user_id.id,
            "start_datetime": datetime.datetime.now(),
        })

        notifications = []
        message = {"status": "play", "active_work_id": self.id, "active_task_id": self.task_id.id, "timelog_id": last_timelog.id}
        notifications.append([(self._cr.dbname, "project.timelog", self.env.user.id), message])
        self.env["bus.bus"].sendmany(notifications)

    @api.multi
    def stop_timer(self):
        if self.env.user.id != self.user_id.id:
            # current user is not match user with solved task
            return False

        timelog = self.env["project.timelog"].search([("work_id", "=", self.id), ("user_id", "=", self.env.user.id)])

        if timelog[-1].end_datetime is not False:
            return False

        # last timelog in current work
        last_timelog_id = timelog[-1].id

        # record date in timer (end datetime for log)
        self.env["project.timelog"].search([("id", '=', last_timelog_id)]).write({
            "end_datetime": datetime.datetime.now(),
        })

        notifications = []
        message = {"status": "stop", "active_work_id": self.id, "active_task_id": self.task_id.id}
        notifications.append([(self._cr.dbname, "project.timelog", self.env.user.id), message])
        self.env["bus.bus"].sendmany(notifications)

        sum_timelog = 0.0
        for e in timelog:
            sum_timelog = sum_timelog + e.duration

        if len(timelog) == 1:
            value = {
                "date": timelog[0].end_datetime,
                "hours": float(sum_timelog),
            }
        else:
            value = {
                "hours": float(sum_timelog),
            }

        self.env["project.task.work"].search([("id", "=", self.id)]).write(value)