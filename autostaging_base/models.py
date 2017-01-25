# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import ValidationError


class AutostagingFolder(models.AbstractModel):
    _name = 'autostaging.folder'
    autostaging_enabled = fields.Boolean('Autostaging enabled', default=True)


class AutostagingStage(models.AbstractModel):
    _name = 'autostaging.stage'
    _card_model = 'define_some_card_model'
    _card_stage_id = 'define_some_card_stage_id'
    autostaging_idle_timeout = fields.Integer('Autostagint idle timeout')
    autostaging_enabled = fields.Boolean('Autostaging enabled', default=False)
    # should be defined on inherired model:
    # autostaging_next_stage = fields.Many2one('define_some_card_model')

    @api.multi
    def write(self, vals):
        result = super(AutostagingStage, self).write(vals)
        if not vals.get('autostaging_enabled', True):
            vals['autostaging_idle_timeout'] = 0
        else:
            for r in self:
                domain = [(self._card_stage_id, '=', r.id)]
                self.env[self._card_model].search(domain)._update_autostaging_date()
        return result

    @api.constrains('autostaging_idle_timeout')
    def _check_autostaging_idle_timeout(self):
        if self.autostaging_enabled and self.autostaging_idle_timeout <= 0:
            raise ValidationError(
                "Days limit field value must be greater than 0")


class AutostagingCard(models.AbstractModel):
    _name = 'autostaging.card'
    _field_folder_id = 'define_some_field_folder_id'
    _field_stage_id = 'define_some_field_stage_id'

    autostaging_date = fields.Date(string='Autostaging date', readonly=True)
    autostaging_days_left = fields.Integer(string='Days left', compute='_compute_autostaging_days_left')
    autostaging_enabled = fields.Boolean(compute='_compute_enabled')
    # should be defined on inherired model:
    # autostaging_next_stage = fields.Many2one('STAGE_MODEL', related='_FIELD_STAGE_ID.autostaging_next_stage')

    @api.multi
    def _compute_enabled(self):
        for r in self:
            r._compute_enabled_one()
        return True

    @api.multi
    def _compute_enabled_one(self):
        self.ensure_one()
        if getattr(self, self._field_stage_id).autostaging_enabled and (
                not getattr(self, self._field_folder_id) or
                getattr(self, self._field_folder_id).autostaging_enabled):
            self.autostaging_enabled = True

    @api.multi
    def _get_autostaging_date(self):
        for r in self:
            r._get_autostaging_date_one()
        return True

    @api.multi
    def _get_autostaging_date_one(self):
        self.ensure_one()
        delta = datetime.timedelta(days=getattr(self, self._field_stage_id).autostaging_idle_timeout)
        return (datetime.datetime.strptime(
            self.write_date, DEFAULT_SERVER_DATETIME_FORMAT) + delta).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.multi
    def _update_autostaging_date(self):
        for r in self:
            r._update_autostaging_date_one()
        return True

    @api.multi
    def _update_autostaging_date_one(self):
        self.ensure_one()
        if not self.env.context.get('autostaging_update_date'):
            self.with_context(autostaging_update_date=True).write({'autostaging_date': self._get_autostaging_date()})

    @api.multi
    def write(self, vals):
        result = super(AutostagingCard, self).write(vals)
        self._update_autostaging_date()
        return result

    @api.model
    def create(self, vals):
        result = super(AutostagingCard, self).create(vals)
        result._update_autostaging_date()
        return result

    @api.multi
    def _compute_autostaging_days_left(self):
        for r in self:
            r._compute_autostaging_days_left_one()
        return True

    @api.multi
    def _compute_autostaging_days_left_one(self):
        self.ensure_one()
        today = datetime.datetime.now()
        date_modifications = datetime.datetime.strptime(self.write_date, DEFAULT_SERVER_DATETIME_FORMAT)
        delta = today - date_modifications
        self.autostaging_days_left = getattr(self, self._field_stage_id).autostaging_idle_timeout - delta.days

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
        domain = ['&', '|',
                  ((self._field_folder_id + '.autostaging_enabled'), '=', True),
                  (self._field_folder_id, '=', False),
                  '&', '&',
                  ((self._field_stage_id + '.autostaging_enabled'), '=', True),
                  ((self._field_stage_id + '.next_stage'), '!=', False),
                  ('autostaging_date', '<=', time.strftime('%Y-%m-%d'))]
        cards = self.search(domain)
        for card in cards:
            card.with_context(autostaging=True).write(
                {self._field_stage_id: getattr(card, self._field_stage_id).next_stage.id})
