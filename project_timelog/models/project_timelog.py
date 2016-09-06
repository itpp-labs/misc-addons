# -*- coding: utf-8 -*-
import datetime
import time
from openerp import models, fields, api, SUPERUSER_ID
from openerp.exceptions import Warning
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
    stage_id = fields.Many2one("project.task.type", string="Stage")

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
            self.duration = round(int(round(resultat.total_seconds(),0))/3600.0,3)

class task(models.Model):
    _inherit = ["project.task"]
    datetime_stopline = fields.Datetime(string="Stopline", select=True, track_visibility='onchange', copy=False)
    _track = {
        'datetime_stopline': {
            'project_timelog.mt_timelog_stopline': lambda self, cr, uid, obj, ctx=None: bool(obj.datetime_stopline),
        },
    }

    def stopline_timer(self, cr, uid, context=None):
        task_obj = self.pool.get("project.task")
        user_rec = self.pool["res.users"].browse(cr, uid, uid, context=context)
        task = self.pool.get("project.task").browse(cr, uid, user_rec.active_task_id, context=context)
        if task.datetime_stopline is False:
            return False
        today = datetime.datetime.now()
        stopline_date = datetime.datetime.strptime(task.datetime_stopline, "%Y-%m-%d %H:%M:%S")
        if stopline_date<=today:
            work = self.pool["project.task.work"].browse(cr, uid, user_rec.active_work_id, context=context)
            work.stop_timer(client_status = False, stopline=True) # time limited, call stop function
        else:
            warning_time = stopline_date - datetime.timedelta(minutes=20)
            notifications = []
            time = {
                'year': warning_time.year,
                'month': warning_time.month,
                'day': warning_time.day,
                'minute': warning_time.minute,
            }
            message = {"status": "stopline", "time": time}
            notifications.append([(cr.dbname, "project.timelog", user_rec.id), message])
            self.pool["bus.bus"].sendmany(cr, uid, notifications)
            # не отправляется сообщение через bus, перепроверить
            return True

class Users(models.Model):
    _inherit = ["res.users"]

    active_work_id = fields.Integer(default=0)
    active_task_id = fields.Integer(default=0)
    timer_status = fields.Boolean(default=False)

class project_task_type(models.Model):
    _inherit = ["project.task.type"]

    allow_log_time = fields.Boolean(default=True)


class project_work(models.Model):
    _inherit = ["project.task.work"]
    stage_id = fields.Many2one("project.task.type", "Stage")
    _sql_constraints = [
        ('name_task_uniq', 'unique (name,stage_id,task_id)', 'The name of the subtask must be unique per stage!')
    ]
    timelog_ids = fields.One2many("project.timelog", "work_id", "Timelog")
    status = fields.Char(string="Status", default="active")
    # task_stage = fields.Many2one(related='task_id.stage_id')
    task_allow_logs = fields.Boolean(related='task_id.stage_id.allow_log_time', store=True, default=True)

    def create(self, cr, uid, vals, context=None):
        task = self.pool.get('project.task').browse(cr, uid, vals.get('task_id'), context=context)
        vals['stage_id'] = task.stage_id.id
        if 'hours' in vals and (not vals['hours']):
            vals['hours'] = 0.00
        if 'task_id' in vals:
            cr.execute('update project_task set remaining_hours=remaining_hours - %s where id=%s', (vals.get('hours',0.0), vals['task_id']))
            self.pool.get('project.task').invalidate_cache(cr, uid, ['remaining_hours'], [vals['task_id']], context=context)
        return super(project_work,self).create(cr, uid, vals, context=context)

    @api.multi
    def play_timer(self):
        if self.env.user.id != self.user_id.id:
            return {
                'type': 'ir.actions.client',
                'tag': 'action_warn',
                'name': 'Warning',
                'params': {
                   'title': 'Warning!',
                   'text': 'Current user is not match user with solved task.',
                   'sticky': True
                }
            }

        if self.env.user.timer_status is True:
            return {
                'type': 'ir.actions.client',
                'tag': 'action_warn',
                'name': 'Warning',
                'params': {
                   'title': 'Error!',
                   'text': 'Please, stop previous timer.',
                   'sticky': False
                }
            }
            ''' last_timelog = self.env["project.timelog"].search([("work_id", "=", self.env.user.active_work_id)])[-1]
            last_timelog.write({
                "end_datetime": datetime.datetime.now(),
            })
            self.env["project.task.work"].search([("id", "=", self.env.user.active_work_id)]).write({
                'status':'stop',
            })'''
        project_task = self.env["project.task"].search([("id", "=", self.task_id.id)])
        if len(project_task)>0:
            if project_task.stage_id.allow_log_time is False:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'action_warn',
                    'name': 'Warning',
                    'params': {
                       'title': 'Error!',
                       'text': 'In the current state of the task can not be created timelogs.',
                       'sticky': True
                    }
                }

        if self.stage_id.id != project_task.stage_id.id:
            return {
                'type': 'ir.actions.client',
                'tag': 'action_warn',
                'name': 'Warning',
                'params': {
                    'title': 'Error!',
                    'text': 'Current task stage different from the stage subtasks.',
                    'sticky': True
                }
            }
        datetime_stopline = project_task.datetime_stopline
        if datetime_stopline is not False and self.task_id.id == self.env.user.active_task_id:
            stopline_date = datetime.datetime.strptime(task.datetime_stopline, "%Y-%m-%d %H:%M:%S")
            if stopline_date<=datetime.datetime.now():
                return {
                    'type': 'ir.actions.client',
                    'tag': 'action_warn',
                    'name': 'Warning',
                    'params': {
                       'title': 'Error!',
                       'text': 'Unable to create logs until it is modified or deleted stopline.',
                       'sticky': True
                    }
                }
        stage = project_task.stage_id.id
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
                return {
                    'type': 'ir.actions.client',
                    'tag': 'action_warn',
                    'name': 'Warning',
                    'params': {
                       'title': 'Error!',
                       'text': "Yesterday's timelogs.",
                       'sticky': False
                    }
                }

        self.write({'status':'play'})

        # record data for current user (last active timer)
        current_user.write({
            "active_work_id": self.id,
            "active_task_id": self.task_id.id,
            "timer_status": True,
        })

        # create new timelog for current work
        last_timelog = self.env['project.timelog'].create({
            "work_id": self.id,
            "user_id": self.user_id.id,
            "start_datetime": datetime.datetime.now(),
            "stage_id": stage,
        })

        notifications = []
        message = {"status": "play", "active_work_id": self.id, "active_task_id": self.task_id.id, "timelog_id": last_timelog.id}
        notifications.append([(self._cr.dbname, "project.timelog", self.env.user.id), message])
        self.env["bus.bus"].sendmany(notifications)

    @api.multi
    def stop_timer(self, status = False, client_status = True, stopline=False):
        if self.env.user.id != self.user_id.id:
            # current user is not match user with solved task
            return {
                'type': 'ir.actions.client',
                'tag': 'action_warn',
                'name': 'Warning',
                'params': {
                   'title': 'Warning!',
                   'text': 'Current user is not match user with solved task.',
                   'sticky': True
                }
            }

        timelog = self.env["project.timelog"].search([("work_id", "=", self.id), ("user_id", "=", self.env.user.id)])

        if timelog[-1].end_datetime is not False:
            return {
                'type': 'ir.actions.client',
                'tag': 'action_warn',
                'name': 'Warning',
                'params': {
                   'title': 'Warning!',
                   'text': 'The timer already has stopped.',
                   'sticky': False
                }
            }

        if status is True:
            self.write({'status':'nonactive'})
        else:
            self.write({'status':'stop'})

        # last timelog in current work
        last_timelog_id = timelog[-1].id

        # record date in timer (end datetime for log)
        self.env["project.timelog"].search([("id", '=', last_timelog_id)]).write({
            "end_datetime": datetime.datetime.now(),
        })

        notifications = []
        message = {"status": "stop", "active_work_id": self.id, "active_task_id": self.task_id.id, "client_status": client_status, "stopline": stopline}
        notifications.append([(self._cr.dbname, "project.timelog", self.env.user.id), message])
        self.env["bus.bus"].sendmany(notifications)

        self.env["res.users"].search([("id", "=", self.user_id.id)]).write({"timer_status": False})

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

    # This function is called every day for 00:00:00 hours
    def subtask_new_status(self, cr, uid, context=None):
        status_obj = self.pool.get("project.task.work")
        status_ids = self.pool.get("project.task.work").search(cr, uid, [])
        for id in status_ids:
            res = status_obj.browse(cr, uid, id ,context=context)
            if str(res.status) != "nonactive":
                res.write({"status": "nonactive"})
        return True

class im_chat_presence(models.Model):
    _inherit = ["im_chat.presence"]

    # This function is called every 5 minut
    def offline_stop_timer(self, cr, uid, context=None):
        status_obj = self.pool.get("im_chat.presence")
        status_ids = self.pool.get("im_chat.presence").search(cr, uid, [])

        task_obj = self.pool["project.task.work"]
        user_rec = self.pool["res.users"].browse(cr, uid, uid ,context=context)
        for id in status_ids:
            res = status_obj.browse(cr, uid, id ,context=context)

            #  if user offline - call stop timer
            if str(res.status) == "offline":
                task_obj.browse(cr, uid, user_rec.active_work_id ,context=context).stop_timer(client_status = False)

            all_timelog_obj = self.pool["project.timelog"]
            all_timelog_ids =  self.pool["project.timelog"].search(cr, uid, [("work_id", "=", user_rec.active_work_id)])
            last_timelog_obj = all_timelog_obj.browse(cr, uid, all_timelog_ids[-1] ,context=context)
            sum_time = datetime.timedelta(0)

            #  if time a subtask >= all time for log then call stop timer
            if last_timelog_obj.end_datetime is False: # pressed button "play"
                time_now = datetime.datetime.now()
                sum_time = sum_time + (time_now - datetime.datetime.strptime(last_timelog_obj.start_datetime, "%Y-%m-%d %H:%M:%S"))
                for id in all_timelog_ids[:-1]:
                    timelog_obj = all_timelog_obj.browse(cr, uid, id ,context=context)
                    date_start_object = datetime.datetime.strptime(timelog_obj.start_datetime, "%Y-%m-%d %H:%M:%S")
                    date_end_object = datetime.datetime.strptime(timelog_obj.end_datetime, "%Y-%m-%d %H:%M:%S")
                    sum_time = sum_time + (date_end_object-date_start_object)
                sum_time = int(round(sum_time.total_seconds(),0))
                time_subtask = int(round(float(self.pool("ir.config_parameter").get_param(cr, uid, 'project_timelog.time_subtasks', context=context))*3600, 0))
                if sum_time >=time_subtask:
                    task_obj.browse(cr, uid, user_rec.active_work_id ,context=context).stop_timer(client_status = False)
        return True