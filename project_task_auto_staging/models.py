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

    to_stage_automove_id = fields.Many2one('project.task.type')
    delay_automove = fields.Integer()
    active_move = fields.Boolean('Enable auto move', default=False)

    @api.onchange('active_move')
    def _onchange_active_move(self):
        if not self.active_move:
            self.delay_automove = 0
        else:
            self.delay_automove = 30

    @api.one
    @api.constrains('delay_automove')
    def _check_delay_automove(self):
        if self.active_move and self.delay_automove <= 0:
            raise ValidationError(
                "Value of 'Delay' field  must be greater than 0")


class project_task_auto_staging(models.Model):
    _inherit = 'project.task'
    allow_automove = fields.Boolean(compute='_get_allow_automove')
    delay_automove = fields.Integer(
        string='Delay', related='stage_id.delay_automove', readonly=True)
    automove_to_stage_id = fields.Many2one(
        'project.task.type', readonly=True,
        related='stage_id.to_stage_automove_id')
    when_date_automove = fields.Date(
        string='When', compute='_get_when_date_automove')
    days_to_automove = fields.Integer(
        string='Days to automove', compute='_get_days_to_automove',
        track_visibility='always')
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
    def _get_when_date_automove(self):
        delta = datetime.timedelta(days=self.delay_automove)
        self.when_date_automove = datetime.datetime.strptime(
            self.write_date, DEFAULT_SERVER_DATETIME_FORMAT) + delta

    @api.one
    def _get_days_to_automove(self):
        if self.allow_automove:
            today = datetime.datetime.now()
            date_modifications = datetime.datetime.strptime(
                self.write_date, DEFAULT_SERVER_DATETIME_FORMAT)
            delta = today - date_modifications
            self.days_to_automove = self.delay_automove - delta.days
        else:
            self.days_to_automove = -1

    @api.model
    def _cron_move_tasks(self):
        today = fields.Date.context_today(self)
        pt_env = self.env['project.task']
        tasks = pt_env.search([])
        for task in tasks:
            if task.allow_automove and today == task.when_date_automove:
                task.with_context(auto_staging=True).write(
                    {'stage_id':  task.automove_to_stage_id.id})
