# -*- coding: utf-8 -*-
import re
from datetime import timedelta
import base64
from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import logging
_logger = logging.getLogger(__name__)
try:
    from icalendar import Calendar
except ImportError:
    _logger.debug('icalendar library missing. Install it via "pip install icalendar"')


class HrPublicHolidaysImportIcs(models.TransientModel):
    _name = "hr_public_holidays.import_ics_wizard"

    ics_file = fields.Binary(string='Selected file', filters="*.ics", required=True)
    ics_file_name = fields.Char()

    @api.multi
    def import_ics(self):
        ics = base64.b64decode(self.ics_file)
        lines = []
        for event in Calendar.from_ical(ics).walk('vevent'):
            dtend = event.get('dtend').dt
            dtstart = event.get('dtstart').dt
            day_count = (dtend - dtstart).days
            if day_count > 1:
                for dt in (dtstart + timedelta(n) for n in range(day_count)):
                    lines.extend([(0, 0, {'name': event.get('summary'), 'date': dt.strftime(DF)})])
            else:
                lines.extend([(0, 0, {'name': event.get('summary'), 'date': dtstart.strftime(DF)})])
        if lines:
            holidays = self.env['hr.holidays.public'].browse(self._context.get('active_id', []))
            holidays.write({'line_ids': lines})

    @api.onchange('ics_file_name')
    def _onchange_ics_file_name(self):
        if self.ics_file_name:
            if not re.match(r'.*\.ics$', self.ics_file_name):
                raise Warning("Please select *.ics file")
