# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class project_project_auto_staging(models.Model):
    _inherit = 'project.project'
    allow_automove = fields.Boolean('Allow automove', default=False)


class autostaging(models.Model):
    _name = 'project_task_auto_staging.autostaging'

    testing_stage = fields.Char(string='Testing Stage')
    done_stage = fields.Char(string='Done Stage')
    cancell_stage = fields.Char(string='Cancell Stage')
    delay_done = fields.Integer(string='Delay Done Stage')
    delay_cancell = fields.Integer(string='Delay Cancel Stage')


class project_task_auto_staging(models.Model):
    _inherit = 'project.task'
    allow = fields.Boolean(compute='_get_allow')
    delay = fields.Integer(
        string='Delay', compute='_get_delay_done')
    to_stage = fields.Char(
        string='To stage', compute='_get_stage')
    when_date = fields.Date(
        string='When', compute='_get_when_date')

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

    @api.one
    def _get_when_date(self):
        delta = datetime.timedelta(days=self.delay)
        self.when_date = datetime.datetime.strptime(
            self.write_date, DEFAULT_SERVER_DATETIME_FORMAT) + delta

    @api.one
    def _get_allow(self):
        as_env = self.env['project_task_auto_staging.autostaging']
        records = as_env.search([])
        if not self.project_id.allow_automove or \
           self.stage_id.name == records[0].done_stage or \
           self.stage_id.name == records[0].cancell_stage:
            self.alow = False
        else:
            self.allow = True

    @api.one
    def _get_delay_done(self):
        as_env = self.env['project_task_auto_staging.autostaging']
        records = as_env.search([])
        if self.stage_id.name == records[0].testing_stage:
            self.delay = records[0].delay_done
        else:
            self.delay = records[0].delay_cancell

    @api.one
    def _get_stage(self):
        as_env = self.env['project_task_auto_staging.autostaging']
        records = as_env.search([])
        if self.stage_id.name == records[0].testing_stage:
            self.to_stage = records[0].done_stage
        else:
            self.to_stage = records[0].cancell_stage

    @api.model
    def get_rest_day(self, write_date):
        today = datetime.datetime.now()
        last_date = datetime.datetime.strptime(
            write_date, DEFAULT_SERVER_DATETIME_FORMAT)
        delta = today - last_date
        return delta.days
