# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import ValidationError


class project_project_auto_staging(models.Model):
    _inherit = 'project.project'
    allow_automove = fields.Boolean('Allow auto move', default=False)


class project_task_type_auto_staging(models.Model):
    _inherit = 'project.task.type'

    to_stage_id = fields.Many2one('project.task.type')
    delay = fields.Integer(default=12)
    active_move = fields.Boolean('Enable auto move', default=False)

    @api.one
    @api.constrains('delay')
    def _check_delay(self):
        if self.delay <= 0:
            raise ValidationError(
                "Value of 'Delay' field  must be greater than 0")


class project_task_auto_staging(models.Model):
    _inherit = 'project.task'
    allow = fields.Boolean(compute='_get_allow')
    delay = fields.Integer(
        string='Delay', compute='_get_delay')
    to_stage = fields.Char(
        string='To stage', compute='_get_stage')
    when_date = fields.Date(
        string='When', compute='_get_when_date')

    @api.one
    def _get_allow(self):
        self.allow = self.project_id.use_tasks and \
            self.project_id.allow_automove and \
            self.stage_id.active_move and self.stage_id.to_stage_id

    @api.one
    def _get_delay(self):
        self.delay = self.stage_id.delay

    @api.one
    def _get_stage(self):
        self.to_stage = self.stage_id.to_stage_id.name

    @api.one
    def _get_when_date(self):
        delta = datetime.timedelta(days=self.delay)
        self.when_date = datetime.datetime.strptime(
            self.write_date, DEFAULT_SERVER_DATETIME_FORMAT) + delta

    @api.model
    def get_rest_day(self, write_date):
        today = datetime.datetime.now()
        last_date = datetime.datetime.strptime(
            write_date, DEFAULT_SERVER_DATETIME_FORMAT)
        delta = today - last_date
        return delta.days

    def _create_msg_and_notify(self, task, recipients):
        body = "<strong>Autostaging:</strong> Task {0} of project {1}\
            moved in {2} stage".format(
            task.name, task.project_id.name, task.stage_id.name)
        message_vals = {
            'body': body,
            'date': datetime.datetime.now(),
            'res_id': task.id,
            'record_name': 'Autostaging task',
            'model': 'project.task',
            'type': 'notification',
            'notified_partner_ids': recipients,
        }
        mail_message = self.env['mail.message']
        msg = mail_message.sudo().create(message_vals)

    def _move_to_stage(self, task):
            ptt_env = self.env['project.task.type']
            stage = ptt_env.search([['name', '=', task.to_stage]])
            task.write({'stage_id': stage.id})

    def _get_notify_users(self):
        rg_env = self.env['res.groups']
        records = rg_env.search(
            [('name', '=', 'Manager'), ('category_id.name', '=', 'Project')])
        record = records.ensure_one()
        users = [(4, u.partner_id.id) for u in record.users]
        return users

    @api.model
    def _cron_move_tasks(self):
        today = fields.Date.context_today(self)
        pt_env = self.env['project.task']
        tasks = pt_env.search([])
        notify_users = self._get_notify_users()
        print "IR_CRON: project_task_auto_staging start"
        for task in tasks:
            if task.allow and today == task.when_date:
                self._move_to_stage(task)
                self._create_msg_and_notify(task, notify_users)
        print "IR_CRON: project_task_auto_staging done"
