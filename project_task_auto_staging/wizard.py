# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError


class Wizard(models.TransientModel):
    _name = 'project_task_auto_staging.wizard'

    def _default_settings(self, name):
        result = {}
        as_env = self.env['project_task_auto_staging.autostaging']
        tt_env = self.env['project.task.type']
        records = as_env.search([])
        rec = records[0]
        if name == 'Testing':
            result = tt_env.search([['name', '=', rec.testing_stage]])
        elif name == 'Done':
            result = tt_env.search([['name', '=', rec.done_stage]])
        elif name == 'Cancell':
            result = tt_env.search([['name', '=', rec.cancell_stage]])
        elif name == 'delay done':
            result = rec.delay_done
        elif name == 'delay cancell':
            result = rec.delay_cancell
        return result

    def _default_testing(self):
        return self._default_settings(name='Testing')

    def _default_done(self):
        return self._default_settings(name='Done')

    def _default_cancell(self):
        return self._default_settings(name='Cancell')

    def _default_delay_done(self):
        return self._default_settings(name='delay done')

    def _default_delay_cancell(self):
        return self._default_settings(name='delay cancell')

    testing_stage_id = fields.Many2one(
        'project.task.type',
        required=True,
        default=_default_testing)
    done_stage_id = fields.Many2one(
        'project.task.type',
        required=True,
        default=_default_done)
    cancell_stage_id = fields.Many2one(
        'project.task.type',
        required=True,
        default=_default_cancell)
    delay_done = fields.Integer(
        required=True, default=_default_delay_done)
    delay_cancell = fields.Integer(
        required=True, default=_default_delay_cancell)

    @api.one
    @api.constrains('delay_done', 'delay_cancell')
    def _check_delay(self):
        if self.delay_done <= 0 or self.delay_cancell <= 0:
            raise ValidationError(
                "Value of 'Delay' field  must be greater than 0")

    @api.multi
    def btn_confirm(self):
        result = {}
        as_env = self.env['project_task_auto_staging.autostaging']
        records = as_env.search([])
        autostaging_data = {
            'testing_stage': self.testing_stage_id.name,
            'done_stage': self.done_stage_id.name,
            'cancell_stage': self.cancell_stage_id.name,
            'delay_done': self.delay_done,
            'delay_cancell': self.delay_cancell,
        }
        return records[0].write(autostaging_data)
