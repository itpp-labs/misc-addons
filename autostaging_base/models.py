# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import ValidationError


class AutostagingFolder(models.AbstractModel):
    _name = 'autostaging.folder'
    allow_automove = fields.Boolean('Allow auto move tasks', default=True,
                                    help='Allows move tasks to another stages according to Autostaging settings')


class AutostagingStage(models.AbstractModel):
    _name = 'autostaging.stage'
    delay_automove = fields.Integer()
    active_move = fields.Boolean('Enable auto move', default=False)

    @api.one
    def write(self, vals):
        if not vals.get('active_move', True):
            vals['delay_automove'] = 0
        return super(AutostagingStage, self).write(vals)

    @api.one
    @api.constrains('delay_automove')
    def _check_delay_automove(self):
        if self.active_move and self.delay_automove <= 0:
            raise ValidationError(
                "Value of 'Delay' field  must be greater than 0")


class AutostagingTask(models.AbstractModel):
    _name = 'autostaging.task'
    _field_project_id = 'project_id'
    _field_stage_id = 'stage_id'

    when_date_automove = fields.Date(string='When', readonly=True)
    days_to_automove = fields.Integer(string='Time left', compute='_get_days_to_automove')

    @api.one
    def _get_when_date_automove(self):
        delta = datetime.timedelta(days=getattr(self, self._field_stage_id).delay_automove)
        return (datetime.datetime.strptime(
            self.write_date, DEFAULT_SERVER_DATETIME_FORMAT) + delta).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.one
    def write(self, vals):
        result = super(AutostagingTask, self).write(vals)
        if not self.env.context.get('auto_staging_write'):
            self.with_context(auto_staging_write=True).write({'when_date_automove': self._get_when_date_automove()})
        return result

    @api.one
    def _get_days_to_automove(self):
        today = datetime.datetime.now()
        date_modifications = datetime.datetime.strptime(self.write_date, DEFAULT_SERVER_DATETIME_FORMAT)
        delta = today - date_modifications
        self.days_to_automove = getattr(self, self._field_stage_id).delay_automove - delta.days

    def _get_model_list(self):
        res = []
        for r in self.env['ir.model.fields'].search([('name', '=', 'automove_to_field_stage_id')]):
            res.append(r.model_id.model)
        return res

    @api.model
    def _cron_move_tasks(self):
        for mdl in self._get_model_list():
            self.env[mdl]._move_tasks()

    @api.model
    def _move_tasks(self):
        tasks = self.search([
            ((self._field_project_id + '.allow_automove'), '=', True),
            ((self._field_stage_id + '.active_move'), '=', True),
            ((self._field_stage_id + '.to_stage_automove_id'), '!=', False),
            ('when_date_automove', '<=', time.strftime('%Y-%m-%d'))])
        print tasks, [
            ((self._field_project_id + '.allow_automove'), '=', True),
            ((self._field_stage_id + '.active_move'), '=', True),
            ((self._field_stage_id + '.to_stage_automove_id'), '!=', False),
            ('when_date_automove', '<=', time.strftime('%Y-%m-%d'))]
        for task in tasks:
            task.with_context(auto_staging=True).write(
                {self._field_stage_id:  getattr(task, self._field_stage_id).next_stage.id})
