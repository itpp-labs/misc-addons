# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import ValidationError
from openerp.tools.translate import _


class project_project_auto_staging(models.Model):
    _inherit = 'project.project'
    allow_automove = fields.Boolean('Allow auto move', default=False)


class project_task_type_auto_staging(models.Model):
    _inherit = 'project.task.type'

    to_stage_automove_id = fields.Many2one('project.task.type')
    delay_automove = fields.Integer(default=12)
    active_move = fields.Boolean('Enable auto move', default=False)

    @api.one
    @api.constrains('delay_automove')
    def _check_delay_automove(self):
        if self.active_move and self.delay_automove <= 0:
            raise ValidationError(
                "Value of 'Delay' field  must be greater than 0")
        elif not self.active_move:
            if self.delay_automove < 0:
                self.delay_automove = -self.delay_automove
            elif self.delay_automove == 0:
                self.delay_automove = 12


class project_task_auto_staging(models.Model):
    _inherit = 'project.task'
    allow_automove = fields.Boolean(compute='_get_allow_automove')
    delay_automove = fields.Integer(
        string='Delay', compute='_get_delay_automove')
    to_stage_automove = fields.Char(
        string='To stage', compute='_get_stage')
    when_date_automove = fields.Date(
        string='When', compute='_get_when_date_automove')

    _track = {
        'stage_id': {
            'project_task_auto_staging.mt_auto_move':
            lambda self, cr, uid, obj, ctx=None:
                ctx and ctx.get('auto_staging')
        }
    }

    @api.one
    def _get_allow_automove(self):
        self.allow_automove = self.project_id.use_tasks and \
            self.project_id.allow_automove and \
            self.stage_id.active_move and self.stage_id.to_stage_automove_id

    @api.one
    def _get_delay_automove(self):
        self.delay_automove = self.stage_id.delay_automove

    @api.one
    def _get_stage(self):
        self.to_stage_automove = self.stage_id.to_stage_automove_id.name

    @api.one
    def _get_when_date_automove(self):
        delta = datetime.timedelta(days=self.delay_automove)
        self.when_date_automove = datetime.datetime.strptime(
            self.write_date, DEFAULT_SERVER_DATETIME_FORMAT) + delta

    @api.model
    def get_rest_day(self, write_date):
        today = datetime.datetime.now()
        last_date = datetime.datetime.strptime(
            write_date, DEFAULT_SERVER_DATETIME_FORMAT)
        delta = today - last_date
        return delta.days

    @api.model
    def get_today(self):
        return fields.Datetime.now()

    def _create_msg_and_notify(self, task, recipients, prev_stage):
        body = _("Auto moved <br/>%s -> %s<br/> after %s days of last changes") % \
            (prev_stage, task.stage_id.name, task.delay_automove)
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
        stage = ptt_env.search([['name', '=', task.to_stage_automove]])
        prev_stage = task.stage_id.name
        task.with_context(auto_staging=True).write({'stage_id': stage.id})
        return prev_stage

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
            if task.allow_automove and today == task.when_date_automove:
                prev_stage = self._move_to_stage(task)
                self._create_msg_and_notify(task, notify_users, prev_stage)
        print "IR_CRON: project_task_auto_staging done"
