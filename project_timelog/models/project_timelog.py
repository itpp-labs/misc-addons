# -*- coding: utf-8 -*-
import datetime

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _

from odoo.addons.bus.models.bus_presence import AWAY_TIMER, DISCONNECTION_TIMER


class ProjectTimelog(models.Model):
    _name = "project.timelog"
    _description = "project timelog"
    _rec_name = "work_id"

    work_id = fields.Many2one(
        "account.analytic.line", "Task", required=True, index=True
    )
    task_name = fields.Char(related="work_id.task_id.name", store=True)
    task_id = fields.Many2one(related="work_id.task_id")
    work_name = fields.Char(related="work_id.name", store=True)
    project_name = fields.Char(related="work_id.task_id.project_id.name", store=True)
    start_datetime = fields.Datetime(
        string="Start date", default=datetime.datetime.now()
    )
    end_datetime = fields.Datetime(string="End date")
    end_datetime_active = fields.Datetime(
        string="End date",
        help="End tate. Equal to now if timer is not stopped yet.",
        compute="_compute_end_datetime_active",
    )
    duration = fields.Float(string="Duration", compute="_compute_duration", store=True)
    corrected_duration = fields.Float(
        string="Corrected duration", compute="_compute_corrected_duration", store=True
    )
    corrected_duration_active = fields.Float(string="Corrected duration", store="True")
    user_id = fields.Many2one("res.users", string="User name", index=True)
    stage_id = fields.Many2one("project.task.type", string="Stage")
    time_correction = fields.Float("Time Correction", default=0.00)

    @api.multi
    @api.depends("end_datetime")
    def _compute_end_datetime_active(self):
        for r in self:
            r.end_datetime_active = r.end_datetime or datetime.datetime.now()

    @api.multi
    @api.depends("start_datetime", "end_datetime")
    def _compute_duration(self):
        for r in self:
            r.duration = self._duration(r.start_datetime, r.end_datetime)

    @api.multi
    @api.depends("start_datetime", "end_datetime", "time_correction")
    def _compute_corrected_duration(self):
        for r in self:
            r.corrected_duration = r.duration + r.time_correction

    @api.multi
    def _recompute_corrected_duration_active(self):
        for r in self:
            if r.end_datetime:
                value = r.corrected_duration
            else:
                value = (
                    self._duration(r.start_datetime, datetime.datetime.now())
                    + r.time_correction
                )
            r.corrected_duration_active = value

    @api.model
    def _duration(self, start_datetime, end_datetime):
        if not end_datetime:
            return 0

        if type(start_datetime) is str:
            start_datetime = datetime.datetime.strptime(
                start_datetime, "%Y-%m-%d %H:%M:%S"
            )

        if type(end_datetime) is str:
            end_datetime = datetime.datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S")

        delta = end_datetime - start_datetime
        return delta.total_seconds() / 3600.0

    @api.multi
    def write(self, vals):
        if "time_correction" in vals:
            user = self.env.user
            if not user.has_group("project.group_project_manager"):
                if vals["time_correction"] > 0.00:
                    raise UserError(_("Only manager can enter positive time."))
        for r in self:
            if any(
                [
                    key in vals and getattr(r, key)
                    for key in ["start_datetime", "end_datetime"]
                ]
            ):
                raise UserError(
                    _("Dates cannot be changed. Use Time Correction field instead.")
                )
        return super(ProjectTimelog, self).write(vals)

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        if "corrected_duration_active" in fields:
            recompute_domain = [("end_datetime", "=", False)] + domain
            ids = self.search(recompute_domain)
            ids._recompute_corrected_duration_active()
        return super(ProjectTimelog, self).read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )


class Task(models.Model):
    _inherit = "project.task"

    datetime_stopline = fields.Datetime(
        string="Stopline", index=True, track_visibility="onchange", copy=False
    )
    _track = {
        "datetime_stopline": {
            "project_timelog.mt_timelog_stopline": lambda self, cr, uid, obj, ctx=None: bool(
                obj.datetime_stopline
            )
        }
    }

    @api.model
    def clear_stopline_datetime(self):
        tasks = self.env["project.task"].search(["datetime_stopline", "!=", False])
        for task in tasks:
            datetime_stopline = datetime.datetime.strptime(
                task.datetime_stopline, "%Y-%m-%d %H:%M:%S"
            )
            if datetime_stopline.day < datetime.datetime.today().day:
                task.write({"datetime_stopline": False})

    @api.model
    def stopline_timer(self):
        user = self.env["res.users"].search([])
        for u in user:
            task = u.active_task_id
            if task.datetime_stopline is False:
                return False
            stopline_date = datetime.datetime.strptime(
                task.datetime_stopline, "%Y-%m-%d %H:%M:%S"
            )
            if stopline_date <= datetime.datetime.today():
                u.active_work_id.sudo(u).stop_timer(play_a_sound=False, stopline=True)
                if u.active_work_id.status != "nonactive":
                    u.active_work_id.sudo(u).write({"status": "nonactive"})
            else:
                warning_time = stopline_date - datetime.timedelta(minutes=20)
                notifications = []
                time = {
                    "year": warning_time.year,
                    "month": warning_time.month,
                    "day": warning_time.day,
                    "minute": warning_time.minute,
                }
                message = {"status": "stopline", "time": time}
                channel = '["{}","{}","{}"]'.format(
                    self._cr.dbname, "project.timelog", u.id
                )
                notifications.append([channel, message])
                self.env["bus.bus"].sendmany(notifications)
                return True

    @api.multi
    def set_stage_timer(self):
        for r in self:
            works = r.timesheet_ids.filtered(lambda x: x.status == "play")
            if len(works) == 0:
                return False
            for w in works:
                if r.stage_id == w.stage_id:  # stage is not changed
                    return False

                # stop current timer
                w.sudo(w.user_id).stop_timer()

                if not r.stage_id.allow_log_time:
                    continue

                existing_work = works.search(
                    [
                        ("task_id", "=", r.id),
                        ("name", "=", w.name),
                        ("stage_id", "=", r.stage_id.id),
                    ]
                )
                current_date = datetime.datetime.now()
                subtask_name = ""
                if len(existing_work) > 0:
                    if existing_work.user_id.id == w.user_id.id:
                        new_work = existing_work
                        if (
                            new_work.timelog_ids[0].end_datetime is not False
                        ):  # there are timelogs yesterday
                            date_object = datetime.datetime.strptime(
                                new_work.timelog_ids[0].end_datetime,
                                "%Y-%m-%d %H:%M:%S",
                            )
                            if (
                                date_object is not False
                                and date_object.day != current_date.day
                            ):
                                subtask_name = (
                                    str(current_date.day)
                                    + "."
                                    + str(current_date.month)
                                    + "."
                                    + str(current_date.year)
                                    + " "
                                    + w.name
                                )
                    else:
                        subtask_name = (
                            str(current_date.day)
                            + "."
                            + str(current_date.month)
                            + "."
                            + str(current_date.year)
                            + " "
                            + w.name
                        )
                else:
                    # create new subtask
                    subtask_name = w.name

                if subtask_name:
                    vals = {
                        "name": subtask_name,
                        "task_id": w.task_id.id,
                        "user_id": w.user_id.id,
                        "company_id": w.company_id.id,
                        "account_id": w.account_id.id,
                    }
                    new_work = r.env["account.analytic.line"].sudo().create(vals)

                # run exist timer
                new_work.sudo(w.user_id).play_timer()


class Users(models.Model):
    _inherit = "res.users"

    active_work_id = fields.Many2one("account.analytic.line", "Work", default=None)
    active_task_id = fields.Many2one("project.task", "Task", default=None)
    timer_status = fields.Boolean(default=False)
    im_status = fields.Char(search="_search_im_status")

    def _search_im_status(self, operator, value):
        ids = map(lambda x: x.id, self.env["res.users"].search([]))
        value_ids = []
        self.env.cr.execute(
            """
            SELECT
                user_id as id,
                CASE WHEN age(now() AT TIME ZONE 'UTC', last_poll) > interval %s THEN 'offline'
                     WHEN age(now() AT TIME ZONE 'UTC', last_presence) > interval %s THEN 'away'
                     ELSE 'online'
                END as status
            FROM bus_presence
            WHERE user_id IN %s""",
            ("%s seconds" % DISCONNECTION_TIMER, "%s seconds" % AWAY_TIMER, tuple(ids)),
        )
        res = {status["id"]: status["status"] for status in self.env.cr.dictfetchall()}
        if operator == "=":
            value_ids = [vid for vid in ids if res.get(id, "offline") == value]
        return [("id", "in", value_ids)]

    # This function is called every 5 minutes
    @api.model
    def check_stop_timer(self):
        status = self.env["res.users"].search([("im_status", "=", "offline")])
        for r in status:
            r.active_work_id.sudo(r).stop_timer(play_a_sound=False)
        user = self.search([("active_work_id.status", "=", "play")])
        time_subtask = int(
            round(
                float(
                    self.env["ir.config_parameter"].get_param(
                        "project_timelog.time_subtasks"
                    )
                )
                * 3600,
                0,
            )
        )
        for u in user:
            all_timelog = u.active_work_id.timelog_ids
            sum_time = datetime.timedelta(0)
            for tid in all_timelog:
                date_start_object = datetime.datetime.strptime(
                    tid.start_datetime, "%Y-%m-%d %H:%M:%S"
                )
                date_end_object = (
                    tid.end_datetime
                    and datetime.datetime.strptime(
                        tid.end_datetime, "%Y-%m-%d %H:%M:%S"
                    )
                    or datetime.datetime.now()
                )
                sum_time = sum_time + (date_end_object - date_start_object)
            sum_time = int(round(sum_time.total_seconds(), 0))
            if sum_time >= time_subtask:
                u.active_work_id.sudo(u).stop_timer(play_a_sound=False)
        return True


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    allow_log_time = fields.Boolean(default=True)


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    stage_id = fields.Many2one("project.task.type", "Stage")
    timelog_ids = fields.One2many("project.timelog", "work_id", "Timelog")
    status = fields.Char(string="Status", default="active")
    task_allow_logs = fields.Boolean(related="stage_id.allow_log_time", readonly=True)
    user_current = fields.Boolean(compute="_compute_user_current", default=True)
    project_id = fields.Many2one(
        readonly=True, related="task_id.project_id", store=True
    )

    _sql_constraints = [
        (
            "name_task_uniq",
            "unique (name,stage_id,task_id)",
            "The name of the subtask must be unique per stage!",
        )
    ]

    unit_amount_computed = fields.Float(
        string="Time Spent", compute="_compute_unit_amount", default=0
    )

    combined_name = fields.Char("Task and Summary", compute="_compute_combined_name")

    @api.multi
    def _compute_combined_name(self):
        for r in self:
            r.combined_name = "{}: {}".format(r.task_id.name, r.name)

    @api.multi
    def _compute_user_current(self):
        for r in self:
            if r.user_id.id == r.env.user.id:
                r.user_current = True
            else:
                r.user_current = False

    @api.multi
    @api.depends("timelog_ids.end_datetime", "timelog_ids.time_correction")
    def _compute_unit_amount(self):
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
            r.unit_amount_computed = float(sum_timelog)

    @api.model
    def create(self, vals):
        task = self.env["project.task"].browse(vals.get("task_id"))
        vals["stage_id"] = task.stage_id.id
        if not task.stage_id.allow_log_time:
            raise UserError(
                _('Creating new subtask in state "%s" is forbidden.')
                % task.stage_id.name
            )
        if "user_id" in vals and (not vals["user_id"]):
            vals["user_id"] = self.env.user.id
        if "user_id" not in vals:
            vals["user_id"] = self.env.user.id
        vals["unit_amount_computed"] = 0.00
        if "unit_amount_computed" in vals and (not vals["unit_amount_computed"]):
            vals["unit_amount_computed"] = 0.00
        return super(AccountAnalyticLine, self).create(vals)

    @api.multi
    def write(self, vals):
        unit_amount_computed = (
            vals["unit_amount_computed"]
            if "unit_amount_computed" in vals
            else self.unit_amount_computed
        )
        if (
            "unit_amount" in vals
            and ("task_id" in vals or self.task_id)
            and vals["unit_amount"] > unit_amount_computed
        ):
            vals["unit_amount"] = self.unit_amount
        return super(AccountAnalyticLine, self).write(vals)

    @api.multi
    def play_timer(self):
        if self.env.user.id != self.user_id.id:
            return self.show_warning_message(
                title=_("Warning."),
                message=_("Current user is not match user with solved task."),
            )
        if self.env.user.timer_status is True:
            return self.show_warning_message(
                title=_("Error."), message=_("Please, stop previous timer.")
            )
        project_task = self.task_id
        if project_task:
            if project_task.stage_id.allow_log_time is False:
                return self.show_warning_message(
                    title=_("Error."),
                    message=_(
                        "In the current state of the task can not be created timelogs."
                    ),
                )
        if self.stage_id.id != project_task.stage_id.id:
            return self.show_warning_message(
                title=_("Error."),
                message=_("Current task stage different from the stage subtasks."),
            )

        datetime_stopline = project_task.datetime_stopline
        if (
            datetime_stopline is not False
            and self.task_id.id == self.env.user.active_task_id
        ):
            stopline_date = datetime.datetime.strptime(
                datetime_stopline, "%Y-%m-%d %H:%M:%S"
            )
            if stopline_date <= datetime.datetime.now():
                return self.show_warning_message(
                    title=_("Error."),
                    message=_(
                        "Unable to create logs until it is modified or deleted stopline."
                    ),
                )
        stage = project_task.stage_id.id
        corrected_duration = self.env["project.timelog"].search(
            [("work_id", "=", self.id), ("user_id", "=", self.env.user.id)]
        )
        config = self.env["ir.config_parameter"].get_param(
            "project_timelog.time_subtasks"
        )

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
            date_object = datetime.datetime.strptime(
                first_timelog[0].end_datetime, "%Y-%m-%d %H:%M:%S"
            )
            if date_object is not False and date_object.day != current_date.day:
                # there are timelogs yesterday
                return self.show_warning_message(
                    title=_("Error."), message=_("Yesterday's timelogs.")
                )
        self.write({"status": "play"})

        # record data for current user (last active timer)
        current_user.write(
            {
                "active_work_id": self.id,
                "active_task_id": self.task_id.id,
                "timer_status": True,
            }
        )

        # create new timelog for current work
        last_timelog = self.env["project.timelog"].create(
            {
                "work_id": self.id,
                "user_id": self.user_id.id,
                "start_datetime": datetime.datetime.now(),
                "stage_id": stage,
            }
        )

        notifications = []
        message = {
            "status": "play",
            "active_work_id": self.id,
            "active_task_id": self.task_id.id,
            "timelog_id": last_timelog.id,
        }
        channel = '["{}","{}","{}"]'.format(
            self._cr.dbname, "project.timelog", self.env.user.id
        )
        notifications.append([channel, message])
        self.env["bus.bus"].sendmany(notifications)

    @api.multi
    def stop_timer(self, status=False, play_a_sound=True, stopline=False):
        for r in self:
            if r.env.user.id != r.user_id.id:
                # current user is not match user with solved task
                return self.show_warning_message(
                    title=_("Warning."),
                    message=_("Current user is not match user with solved task."),
                )

            timelog = r.env.user.active_work_id.timelog_ids

            if timelog[-1].end_datetime is not False:
                return self.show_warning_message(
                    title=_("Warning."), message=_("The timer already has stopped.")
                )
            if status is True:
                r.write({"status": "nonactive"})
            else:
                r.write({"status": "stop"})

            # last timelog in current work
            last_timelog_id = timelog[-1].id

            # record date in timer (end datetime for log)
            r.env["project.timelog"].search([("id", "=", last_timelog_id)]).write(
                {"end_datetime": datetime.datetime.now()}
            )

            if self.unit_amount_computed:
                self.unit_amount = self.unit_amount_computed

            notifications = []
            message = {
                "status": "stop",
                "active_work_id": r.id,
                "active_task_id": r.task_id.id,
                "play_a_sound": play_a_sound,
                "stopline": stopline,
            }
            channel = '["{}","{}","{}"]'.format(
                r._cr.dbname, "project.timelog", r.env.user.id
            )
            notifications.append([channel, message])
            r.env["bus.bus"].sendmany(notifications)

            r.user_id.write({"timer_status": False})

            if len(timelog) == 1:
                r.write({"date": timelog[0].end_datetime})

    def show_warning_message(self, title, message):
        return {
            "type": "ir.actions.client",
            "tag": "action_warn",
            "params": {"title": title, "text": message},
        }

    # This function is called every day for 00:00:00 hours
    @api.model
    def subtask_new_status(self):
        status = self.env["account.analytic.line"].search(
            [("status", "!=", "nonactive")]
        )
        for e in status:
            e.sudo(e.user_id).write({"status": "nonactive"})
        return True
