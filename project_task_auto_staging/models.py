# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import ValidationError


class ProjectProjectAutoStaging(models.Model):
    _inherit = 'project.project'
    allow_automove = fields.Boolean('Allow auto move tasks', default=True, help='Allows move tasks to another stages according to Autostaging settings')


class ProjectTaskTypeAutoStaging(models.Model):
    _inherit = 'project.task.type'

    to_stage_automove_id = fields.Many2one('project.task.type')
    delay_automove = fields.Integer()
    active_move = fields.Boolean('Enable auto move', default=False)

    @api.multi
    def write(self, vals):
        if not vals.get('active_move', True):
            vals['delay_automove'] = 0
        return super(ProjectTaskTypeAutoStaging, self).write(vals)

    @api.one
    @api.constrains('delay_automove')
    def _check_delay_automove(self):
        if self.active_move and self.delay_automove <= 0:
            raise ValidationError(
                "Value of 'Delay' field  must be greater than 0")


class ProjectTaskAutoStaging(models.Model):
    _inherit = 'project.task'
    allow_automove = fields.Boolean(
        compute='_get_allow_automove', search='_search_allow_automove')
    delay_automove = fields.Integer(
        string='Delay', related='stage_id.delay_automove', readonly=True)
    automove_to_stage_id = fields.Many2one(
        'project.task.type', readonly=True,
        related='stage_id.to_stage_automove_id')
    when_date_automove = fields.Date(
        string='When', compute='_get_when_date_automove', store=True)
    days_to_automove = fields.Integer(
        string='Days to automove', compute='_get_days_to_automove')
    _track = {
        'stage_id': {
            'project_task_auto_staging.mt_auto_move_task':
            lambda self, cr, uid, obj, ctx=None:
            ctx and ctx.get('auto_staging')
        }
    }

    def _search_allow_automove(self, operator, value):
        if operator == '=' and value is True:
            return ['&', '&', '&', ('project_id.use_tasks', '=', True),
                    ('project_id.allow_automove', '=', True),
                    ('stage_id.active_move', '=', True),
                    ('stage_id.to_stage_automove_id', '!=', False)]

    @api.multi
    def _get_allow_automove(self):
        for r in self:
            r._get_allow_automove_one()
        return True

    @api.multi
    def _get_allow_automove_one(self):
        self.ensure_one()
        self.allow_automove = self.project_id.use_tasks and \
            self.project_id.allow_automove and \
            self.stage_id.active_move and self.stage_id.to_stage_automove_id

    @api.one
    @api.depends('write_date', 'delay_automove')
    def _get_when_date_automove(self):
        delta = datetime.timedelta(days=self.delay_automove)
        self.when_date_automove = datetime.datetime.strptime(
            self.write_date, DEFAULT_SERVER_DATETIME_FORMAT) + delta

    @api.multi
    def _get_days_to_automove(self):
        for r in self:
            r._get_days_to_automove_one()
        return True

    @api.multi
    def _get_days_to_automove_one(self):
        self.ensure_one()
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
        tasks = self.env['project.task'].search([
            ('allow_automove', '=', True),
            ('when_date_automove', '<=', time.strftime('%Y-%m-%d'))])
        for task in tasks:
            task.with_context(auto_staging=True).write(
                {'stage_id': task.automove_to_stage_id.id})
