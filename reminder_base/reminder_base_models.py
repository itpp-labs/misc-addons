# -*- coding: utf-8 -*-
from openerp import api
from openerp import fields
from openerp import models


class Reminder(models.AbstractModel):
    _name = 'reminder'

    _reminder_date_field = 'date'
    _reminder_description_field = 'description'

    # res.users or res.partner fields
    _reminder_attendees_fields = ['user_id']

    reminder_event_id = fields.Many2one('calendar.event',
                                        string='Reminder Calendar Event')
    reminder_alarm_ids = fields.Many2many('calendar.alarm', string='Reminders',
                                          related='reminder_event_id.alarm_ids')

    @api.multi
    def _get_reminder_event_name(self):
        for r in self:
            r._get_reminder_event_name_one()
        return True

    @api.multi
    def _get_reminder_event_name_one(self):
        self.ensure_one()
        return '%s: %s' % (self._description, self.display_name)

    @api.model
    def _create_reminder_event(self):
        vals = {
            'reminder_res_model': self._name,
            # dummy values
            'name': 'TMP NAME',
            'allday': True,
            'start_date': fields.Date.today(),
            'stop_date': fields.Date.today(),
        }
        event = self.env['calendar.event'].with_context({
            'no_mail_to_attendees': True
        }).create(vals)
        return event

    @api.model
    def _init_reminder(self):
        domain = [(self._reminder_date_field, '!=', False)]
        self.search(domain)._do_update_reminder()

    @api.multi
    def _update_reminder(self, vals):
        for r in self:
            r._update_reminder_one(vals)
        return True

    @api.multi
    def _update_reminder_one(self, vals):
        self.ensure_one()
        if self._context.get('do_not_update_reminder'):
            # ignore own calling of write function
            return
        if not vals:
            return
        if not self.reminder_event_id and self._reminder_date_field not in vals:
            # don't allow to create reminder if date is not set
            return
        fields = ['reminder_alarm_ids',
                  self._reminder_date_field,
                  self._reminder_description_field]
        if not any([k in vals for k in fields if k]):
            return
        self._do_update_reminder(update_date=self._reminder_date_field in vals)

    @api.multi
    def _do_update_reminder(self, update_date=True):
        for r in self:
            r._do_update_reminder_one(update_date=True)
        return True

    @api.multi
    def _do_update_reminder_one(self, update_date=True):
        self.ensure_one()
        vals = {'name': self._get_reminder_event_name()[0]}

        event = self.reminder_event_id
        if not event:
            event = self._create_reminder_event()
            self.with_context(do_not_update_reminder=True).write({'reminder_event_id': event.id})

        if not event.reminder_res_id:
            vals['reminder_res_id'] = self.id

        if update_date:
            fdate = self._fields[self._reminder_date_field]
            fdate_value = getattr(self, self._reminder_date_field)
            if not fdate_value:
                event.unlink()
                return
            if fdate.type == 'date':
                vals.update({
                    'allday': True,
                    'start_date': fdate_value,
                    'stop_date': fdate_value,
                })
            elif fdate.type == 'datetime':
                vals.update({
                    'allday': False,
                    'start_datetime': fdate_value,
                    'stop_datetime': fdate_value,
                })
        if self._reminder_description_field:
            vals['description'] = getattr(self, self._reminder_description_field)

        if self._reminder_attendees_fields:
            partner_ids = []
            for field_name in self._reminder_attendees_fields:
                field = self._columns[field_name]
                partner = getattr(self, field_name)
                model = None
                try:
                    model = field.comodel_name
                except AttributeError:
                    model = field._obj  # v7

                if model == 'res.users':
                    partner = partner.partner_id
                if partner and partner.id not in partner_ids:
                    partner_ids.append(partner.id)
            vals['partner_ids'] = [(6, 0, partner_ids)]

        event.with_context(no_mail_to_attendees=True).write(vals)

    @api.model
    def _check_and_create_reminder_event(self, vals):
        fields = [self._reminder_date_field]

        if any([k in vals for k in fields]):
            event = self._create_reminder_event()
            vals['reminder_event_id'] = event.id
        return vals

    @api.model
    def create(self, vals):
        vals = self._check_and_create_reminder_event(vals)
        res = super(Reminder, self).create(vals)
        res._update_reminder(vals)
        return res

    @api.multi
    def write(self, vals):
        for r in self:
            if not r.reminder_event_id:
                vals = r._check_and_create_reminder_event(vals)
        res = super(Reminder, self).write(vals)
        self._update_reminder(vals)
        return res


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    reminder_res_model = fields.Char('Related Document Model for reminding')
    reminder_res_id = fields.Integer('Related Document ID for reminding')

    @api.multi
    def open_reminder_object(self):
        r = self[0]
        target = self._context.get('target', 'current')
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': r.reminder_res_model,
            'res_id': r.reminder_res_id,
            'views': [(False, 'form')],
            'target': target,
        }


class ReminderAdminWizard(models.TransientModel):
    _name = 'reminder.admin'

    model = fields.Selection(string='Model', selection='_get_model_list', required=True)
    events_count = fields.Integer(string='Count of calendar records', compute='_get_events_count')
    action = fields.Selection(string='Action', selection=[('create', 'Create Calendar Records'), ('delete', 'Delete Calendar Records')],
                              required=True, default='create',)

    def _get_model_list(self):
        res = []
        for r in self.env['ir.model.fields'].search([('name', '=', 'reminder_event_id')]):
            if r.model_id.model == 'reminder':
                # ignore abstract class
                continue
            res.append((r.model_id.model, r.model_id.name))
        return res

    @api.onchange('model')
    @api.multi
    def _get_events_count(self):
        for r in self:
            r._get_events_count_one()
        return True

    @api.multi
    def _get_events_count_one(self):
        self.ensure_one()
        count = 0
        if self.model:
            count = self.env['calendar.event'].search_count([('reminder_res_model', '=', self.model)])
        self.events_count = count

    @api.multi
    def action_execute(self):
        for r in self:
            r.action_execute_one()
        return True

    @api.multi
    def action_execute_one(self):
        self.ensure_one()
        if self.action == 'delete':
            self.env['calendar.event'].search([('reminder_res_model', '=', self.model)]).unlink()
        elif self.action == 'create':
            self.env[self.model]._init_reminder()
