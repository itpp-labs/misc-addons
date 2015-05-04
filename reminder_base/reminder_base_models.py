from openerp import api, models, fields, SUPERUSER_ID


class reminder(models.Model):
    _name = 'reminder'

    _reminder_date_field = 'date'
    _reminder_description_field = 'description'

    reminder_event_id = fields.Many2one('calendar.event',
                                        string='Reminder Calendar Event')
    reminder_alarm_ids = fields.Many2many('calendar.alarm', string='Reminders',
                                          related='reminder_event_id.alarm_ids')

    @api.one
    def _get_reminder_event_name(self):
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
        event = self.env['calendar.event'].create(vals)
        return event

    @api.one
    def _check_update_reminder(self, vals):
        if not vals:
            return False
        fields = ['reminder_alarm_ids',
                  self._reminder_date_field,
                  self._reminder_description_field]
        if not any([k in vals for k in fields if k]):
            return False
        return True

    @api.one
    def _update_reminder(self, vals):
        if not self._check_update_reminder(vals):
            print 'no _update_reminder', vals
            return

        vals = {'name': self._get_reminder_event_name()[0]}

        event = self.reminder_event_id
        if not event.reminder_res_id:
            vals['reminder_res_id'] = self.id

        fdate = self._fields[self._reminder_date_field]
        fdate_value = getattr(self, self._reminder_date_field)
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
        event.write(vals)

    @api.model
    def _check_reminder_event(self, vals):
        fields = ['reminder_alarm_ids',
                  self._reminder_date_field]

        if any([k in vals for k in fields]):
            event = self._create_reminder_event()
            vals['reminder_event_id'] = event.id
        return vals

    @api.model
    def create(self, vals):
        vals = self._check_reminder_event(vals)
        res = super(reminder, self).create(vals)
        res._update_reminder(vals)
        return res

    @api.one
    def write(self, vals):
        if not self.reminder_event_id:
            vals = self._check_reminder_event(vals)
        res = super(reminder, self).write(vals)
        self._update_reminder(vals)
        return res


class calendar_event(models.Model):
    _inherit = 'calendar.event'

    reminder_res_model = fields.Char('Related Document Model for reminding')
    reminder_res_id = fields.Integer('Related Document ID for reminding')
