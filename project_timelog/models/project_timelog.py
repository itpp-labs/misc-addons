# -*- coding: utf-8 -*-
import datetime
import time
from openerp import models, fields, api, SUPERUSER_ID
from openerp import http

class ProjectTimeLog(models.Model):
    _name = "project.timelog"
    _description = "project timelog"

    work_id  = fields.Many2one("project.task.work", "Task", required=True)
    start_datetime = fields.Datetime(string="Start date", default=datetime.datetime.now())
    end_datetime = fields.Datetime(string="End date")
    duration = fields.Char(string="Duration", compute="_compute_duration", store=True)
    user_id = fields.Many2one("res.users", string="User name")

    @api.one
    @api.depends("start_datetime", "end_datetime")
    def _compute_duration(self):
        if self.end_datetime == False:
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
            if (resultat.days == 1):
                out = str(resultat).replace(" day, ", ":")
            elif (resultat.days > 1):
                out = str(resultat).replace(" days, ", ":")
            else:
                out = "0:" + str(resultat)
            outAr = out.split(':')
            outAr = ["%02d" % (int(float(x))) for x in outAr]
            self.duration = ":".join(outAr)

class task(models.Model):
    _inherit = ["project.task"]
    datetime_stopline = fields.Datetime(string="Stopline", select=True, copy=False)

class Users(models.Model):
    _inherit = ["res.users"]

    active_work_id = fields.Integer(default=0)
    active_task_id = fields.Integer(default=0)

class project_work(models.Model):
    _inherit = ["project.task.work"]

    timelog_ids = fields.One2many("project.timelog", "work_id", "Timelog") # ????????

    @api.multi
    def play_timer(self):
        if self.env.user.id != self.user_id.id:
            # current user is not match user with solved task
            return False

        current_user = self.env["res.users"].search([("id", "=", self.user_id.id)])
        current_date = datetime.datetime.now()

        first_timelog = self.env["project.timelog"].search([("work_id", "=", self.id)])

        if len(first_timelog)>0 and first_timelog[0].end_datetime is not False:
            date_object = datetime.datetime.strptime(first_timelog[0].end_datetime, "%Y-%m-%d %H:%M:%S")
            if date_object is not False and date_object.day != current_date.day:
                # there are timelogs yesterday
                return False

        # record data for current user (last active timer)
        current_user.write({
            "active_work_id": self.id,
            "active_task_id": self.task_id.id,
        })

        # create new timelog for current work
        self.env['project.timelog'].create({
            "work_id": self.id,
            "user_id": self.user_id.id,
            "start_datetime": datetime.datetime.now(),
        })

        # notifications = []
        # message = {"play": "play", "active_work_id": self.id, "active_task_id": self.task_id.id}
        # notifications.append([(self._cr.dbname, "chess.game.line", self.env.user.id), message])
        # self.env["bus.bus"].sendmany(notifications)

    @api.multi
    def stop_timer(self):
        if self.env.user.id != self.user_id.id:
            # current user is not match user with solved task
            return False

        timelog = self.env["project.timelog"].search([("work_id", "=", self.id), ("user_id.id", "=", self.env.user.id)])

        # last timelog in current work
        last_timelog_id = timelog[len(timelog)-1].id

        # record date in timer (end datetime for log)
        self.env["project.timelog"].search([("id", '=', last_timelog_id)]).write({
            "end_datetime": datetime.datetime.now(),
        })

        # notifications = []
        # message = {"stop": "stop", "active_work_id": self.id, "active_task_id": self.task_id.id}
        # notifications.append([(self._cr.dbname, "chess.game.line", self.env.user.id), message])
        # self.env["bus.bus"].sendmany(notifications)