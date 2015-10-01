# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import ValidationError


class AutostagingFolder(models.AbstractModel):
    _name = 'autostaging.folder'
    autostaging_support = fields.Boolean('Autostaging support', default=True,
                                         help='Define if your project will support the autostaging functionality')


class AutostagingStage(models.AbstractModel):
    _name = 'autostaging.stage'
    _card_model = 'project.task'
    _card_stage_id = 'stage_id'
    autostaging_days_limit = fields.Integer('Days limit')
    autostaging_enabled = fields.Boolean('Enable', default=False)

    @api.one
    def write(self, vals):
        result = super(AutostagingStage, self).write(vals)
        if not vals.get('autostaging_enabled', True):
            vals['autostaging_days_limit'] = 0
        else:
            domain = [(self._card_stage_id, '=', self.id)]
            self.env[self._card_model].search(domain)._update_autostaging_date()
        return result

    @api.one
    @api.constrains('autostaging_days_limit')
    def _check_autostaging_days_limit(self):
        if self.autostaging_enabled and self.autostaging_days_limit <= 0:
            raise ValidationError(
                "Days limit field value must be greater than 0")


class AutostagingTask(models.AbstractModel):
    _name = 'autostaging.card'
    _field_folder_id = 'project_id'
    _field_stage_id = 'stage_id'

    autostaging_date = fields.Date(string='Autostaging date', readonly=True)
    autostaging_days_left = fields.Integer(string='Days left', compute='_get_autostaging_days_left')

    @api.one
    def _get_autostaging_date(self):
        delta = datetime.timedelta(days=getattr(self, self._field_stage_id).autostaging_days_limit)
        return (datetime.datetime.strptime(
            self.write_date, DEFAULT_SERVER_DATETIME_FORMAT) + delta).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.one
    def _update_autostaging_date(self):
        if not self.env.context.get('autostaging_update_date'):
            self.with_context(autostaging_update_date=True).write({'autostaging_date': self._get_autostaging_date()})

    @api.one
    def write(self, vals):
        result = super(AutostagingTask, self).write(vals)
        self._update_autostaging_date()
        return result

    @api.model
    def create(self, vals):
        result = super(AutostagingTask, self).create(vals)
        self._update_autostaging_date()
        return result

    @api.one
    def _get_autostaging_days_left(self):
        today = datetime.datetime.now()
        date_modifications = datetime.datetime.strptime(self.write_date, DEFAULT_SERVER_DATETIME_FORMAT)
        delta = today - date_modifications
        self.autostaging_days_left = getattr(self, self._field_stage_id).autostaging_days_limit - delta.days

    def _get_model_list(self):
        res = []
        for r in self.env['ir.model.fields'].search([('name', '=', 'next_stage_related')]):
            res.append(r.model_id.model)
        return res

    @api.model
    def _cron_move_cards(self):
        for mdl in self._get_model_list():
            self.env[mdl]._move_cards()

    @api.model
    def _move_cards(self):
        tasks = self.search([
            ((self._field_folder_id + '.autostaging_support'), '=', True),
            ((self._field_stage_id + '.autostaging_enabled'), '=', True),
            ((self._field_stage_id + '.next_stage'), '!=', False),
            ('autostaging_date', '<=', time.strftime('%Y-%m-%d'))])
        for task in tasks:
            task.with_context(auto_staging=True).write(
                {self._field_stage_id:  getattr(task, self._field_stage_id).next_stage.id})
