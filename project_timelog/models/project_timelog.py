# -*- coding: utf-8 -*-
import datetime
from openerp import models, fields, api
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class ProjectTimelog(models.Model):
    _name = "project.timelog"
    _description = "project timelog"
    _rec_name = 'work_id'

    work_id = fields.Many2one("project.task.work", "Task", required=True, index=True)
    task_name = fields.Char(related='work_id.task_id.name', store=True)
    project_name = fields.Char(related='work_id.task_id.project_id.name', store=True)
    start_datetime = fields.Datetime(string="Start date", default=datetime.datetime.now())
    end_datetime = fields.Datetime(string="End date")
    duration = fields.Float(string="Duration", compute="_compute_duration", store=True)
    corrected_duration = fields.Float(string="Corrected duration", compute="_compute_corrected_duration", store=True)
    user_id = fields.Many2one("res.users", string="User name", index=True)
    stage_id = fields.Many2one("project.task.type", string="Stage")
    time_correction = fields.Float(default=0.00)

    @api.multi
    @api.depends("start_datetime", "end_datetime")
    def _compute_duration(self):
        for r in self:
            if r.end_datetime is False:
                r.duration = False
            else:
                if type(r.start_datetime) is str:
                    start_datetime = datetime.datetime.strptime(r.start_datetime, "%Y-%m-%d %H:%M:%S")
                else:
                    start_datetime = r.start_datetime

                if type(r.end_datetime) is str:
                    end_datetime = datetime.datetime.strptime(r.end_datetime, "%Y-%m-%d %H:%M:%S")
                else:
                    end_datetime = r.end_datetime

                resultat = end_datetime - start_datetime
                r.duration = round(int(round(resultat.total_seconds(), 0))/3600.0, 3)

    @api.multi
    @api.depends("start_datetime", "end_datetime", "time_correction")
    def _compute_corrected_duration(self):
        for r in self:
            if r.end_datetime is False:
                r.duration = False
            else:
                if type(r.start_datetime) is str:
                    start_datetime = datetime.datetime.strptime(r.start_datetime, "%Y-%m-%d %H:%M:%S")
                else:
                    start_datetime = r.start_datetime

                if type(r.end_datetime) is str:
                    end_datetime = datetime.datetime.strptime(r.end_datetime, "%Y-%m-%d %H:%M:%S")
                else:
                    end_datetime = r.end_datetime

                resultat = end_datetime - start_datetime
                r.corrected_duration = round(int(round(resultat.total_seconds(), 0))/3600.0, 3) + r.time_correction

    @api.multi
    def write(self, vals):
        if 'time_correction' in vals:
            user = self.env.user
            if not user.has_group('project.group_project_manager'):
                if vals['time_correction'] > 0.00:
                    raise UserError(_('Only manager can enter positive time.'))
        return super(ProjectTimelog, self).write(vals)


class Task(models.Model):
    _inherit = ["project.task"]
    datetime_stopline = fields.Datetime(string="Stopline", select=True, track_visibility='onchange', copy=False)
    _track = {
        'datetime_stopline': {
            'project_timelog.mt_timelog_stopline': lambda self, cr, uid, obj, ctx=None: bool(obj.datetime_stopline),
        },
    }

    @api.model
    def stopline_timer(self):
        user = self.env["res.users"].search([])
        for u in user:
            task = self.env["project.task"].search([('id', '=', u.active_task_id.id)])
            if task.datetime_stopline is False:
                return False
            stopline_date = datetime.datetime.strptime(task.datetime_stopline, "%Y-%m-%d %H:%M:%S")
            if stopline_date <= datetime.datetime.now():
                u.active_work_id.sudo(u).stop_timer(play_a_sound=False, stopline=True)
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
                channel = '["%s","%s","%s"]' % (self._cr.dbname, "project.timelog", u.id)
                notifications.append([channel, message])
                self.env["bus.bus"].sendmany(notifications)
                return True

    @api.multi
    def set_stage_timer(self):
        for r in self:
            works = r.work_ids.filtered(lambda x: x.status == "play")
            if len(works) == 0:
                return False
            for w in works:
                if r.stage_id == w.stage_id:  # stage is not changed
                    return False

                # stop current timer
                w.sudo(w.user_id).stop_timer()

                existing_work = works.search([("task_id", "=", r.id), ("name", "=", w.name), ("stage_id", "=", r.stage_id.id)])
                current_date = datetime.datetime.now()
                subtask_name = ''
                if len(existing_work) > 0:
                    if existing_work.user_id.id == w.user_id.id:
                        new_work = existing_work
                        if new_work.timelog_ids[0].end_datetime is not False:   # there are timelogs yesterday
                            date_object = datetime.datetime.strptime(new_work.timelog_ids[0].end_datetime, "%Y-%m-%d %H:%M:%S")
                            if date_object is not False and date_object.day != current_date.day:
                                subtask_name = str(current_date.day) + '.' + str(current_date.month) + '.' + str(current_date.year) + ' ' + w.name
                    else:
                        subtask_name = str(current_date.day) + '.' + str(current_date.month) + '.' + str(current_date.year) + ' ' + w.name
                else:
                    # create new subtask
                    subtask_name = w.name

                if subtask_name:
                    vals = {
                        'name': subtask_name,
                        'task_id': w.task_id.id,
                        'user_id': w.user_id.id,
                        'company_id': w.company_id.id,
                    }
                    new_work = r.env["project.task.work"].sudo().create(vals)

                new_work.sudo(w.user_id).play_timer()


class Users(models.Model):
    _inherit = ["res.users"]

    active_work_id = fields.Many2one("project.task.work", "Work", default=None)
    active_task_id = fields.Many2one("project.task", "Task", default=None)
    timer_status = fields.Boolean(default=False)


class ProjectTaskType(models.Model):
    _inherit = ["project.task.type"]

    allow_log_time = fields.Boolean(default=True)


class ProjectWork(models.Model):
    _inherit = ["project.task.work"]
    _order = 'id'
    stage_id = fields.Many2one("project.task.type", "Stage")
    _sql_constraints = [
        ('name_task_uniq', 'unique (name,stage_id,task_id)', 'The name of the subtask must be unique per stage!')
    ]
    hours = fields.Float(string='Time Spent', compute="_compute_hours", default=0)
    timelog_ids = fields.One2many("project.timelog", "work_id", "Timelog")
    status = fields.Char(string="Status", default="active")
    task_allow_logs = fields.Boolean(related='task_id.stage_id.allow_log_time', store=True, default=True)
    user_current = fields.Boolean(compute="_compute_user_current", default=True)

    @api.multi
    def _compute_user_current(self):
        for r in self:
            if r.user_id.id == r.env.user.id:
                r.user_current = True
            else:
                r.user_current = False

    @api.multi
    @api.depends("timelog_ids.end_datetime", "timelog_ids.time_correction")
    def _compute_hours(self):
        for r in self:
            if not r.timelog_ids:
                return False
            sum_timelog = 0.00
            timelog = r.env.user.active_work_id.timelog_ids
            if not timelog:
                return False
            if timelog[-1].end_datetime is False:
                timelog = timelog[:-1]
            for e in timelog:
                sum_timelog = sum_timelog + e.corrected_duration
            r.hours = float(sum_timelog)

    @api.model
    def create(self, vals):
        task = self.env['project.task'].browse(vals.get('task_id'))
        vals['stage_id'] = task.stage_id.id
        if 'user_id' in vals and (not vals['user_id']):
            vals['user_id'] = self.env.user.id
        if 'user_id' not in vals:
            vals['user_id'] = self.env.user.id
        vals['hours'] = 0.00
        if 'hours' in vals and (not vals['hours']):
            vals['hours'] = 0.00
        return super(ProjectWork, self).create(vals)

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
        project_task = self.task_id
        if project_task:
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
            stopline_date = datetime.datetime.strptime(datetime_stopline, "%Y-%m-%d %H:%M:%S")
            if stopline_date <= datetime.datetime.now():
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
        corrected_duration = self.env["project.timelog"].search([("work_id", "=", self.id), ("user_id", "=", self.env.user.id)])
        config = self.env["ir.config_parameter"].get_param("project_timelog.time_subtasks")

        sum_timelog = 0.0
        if corrected_duration and config:
            for e in corrected_duration:
                sum_timelog = sum_timelog + round(e.corrected_duration, 3)
            if sum_timelog >= round(float(config), 3):
                return False

        current_user = self.user_id
        current_date = datetime.datetime.now()

        first_timelog = self.env["project.timelog"].search([("work_id", "=", self.id)])

        if first_timelog and first_timelog[0].end_datetime is not False:
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

        self.write({'status': 'play'})

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
        channel = '["%s","%s","%s"]' % (self._cr.dbname, "project.timelog", self.env.user.id)
        notifications.append([channel, message])
        self.env["bus.bus"].sendmany(notifications)

    @api.multi
    def stop_timer(self, status=False, play_a_sound=True, stopline=False):
        for r in self:
            if r.env.user.id != r.user_id.id:
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

            timelog = r.env.user.active_work_id.timelog_ids

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
                r.write({'status': 'nonactive'})
            else:
                r.write({'status': 'stop'})

            # last timelog in current work
            last_timelog_id = timelog[-1].id

            # record date in timer (end datetime for log)
            r.env["project.timelog"].search([("id", '=', last_timelog_id)]).write({
                "end_datetime": datetime.datetime.now(),
            })

            notifications = []
            message = {"status": "stop", "active_work_id": r.id, "active_task_id": r.task_id.id, "play_a_sound": play_a_sound, "stopline": stopline}
            channel = '["%s","%s","%s"]' % (r._cr.dbname, "project.timelog", r.env.user.id)
            notifications.append([channel, message])
            r.env["bus.bus"].sendmany(notifications)

            r.user_id.write({"timer_status": False})

            if len(timelog) == 1:
                r.write({"date": timelog[0].end_datetime})

    # This function is called every day for 00:00:00 hours
    @api.model
    def subtask_new_status(self):
        status = self.env["project.task.work"].search([('status', '!=', 'nonactive')])
        for e in status:
            e.sudo(e.user_id).write({"status": "nonactive"})
        return True


class ImChatPresence(models.Model):
    _inherit = ["im_chat.presence"]

    # This function is called every 5 minut
    @api.model
    def check_stop_timer(self):
        status = self.env["im_chat.presence"].search([('status', '=', 'offline')])
        for e in status:
            task = self.env["project.task.work"].search([("user_id", "=", e.user_id.id)])
            task.sudo(e.user_id).stop_timer(play_a_sound=False)
        user = self.env["res.users"].search([])
        time_subtask = int(round(float(self.env["ir.config_parameter"].get_param('project_timelog.time_subtasks'))*3600, 0))
        for u in user:
            all_timelog = self.env["project.timelog"].search([("work_id", "=", u.active_work_id.id)])
            sum_time = datetime.timedelta(0)
            for id in all_timelog:
                date_start_object = datetime.datetime.strptime(id.start_datetime, "%Y-%m-%d %H:%M:%S")
                date_end_object = id.end_datetime and datetime.datetime.strptime(id.end_datetime, "%Y-%m-%d %H:%M:%S") or datetime.datetime.now()
                sum_time = sum_time + (date_end_object-date_start_object)
            sum_time = int(round(sum_time.total_seconds(), 0))
            if sum_time >= time_subtask:
                u.active_work_id.sudo(u).stop_timer(play_a_sound=False)
        return True
