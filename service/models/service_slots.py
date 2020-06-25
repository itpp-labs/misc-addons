# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from dateutil import parser
from dateutil import rrule
from dateutil.relativedelta import relativedelta
import logging
from operator import itemgetter
import time
import uuid

from odoo import api, fields, models
from odoo import tools
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)

VIRTUALID_DATETIME_FORMAT = "%Y%m%d%H%M%S"


class ListSetup(models.Model):

    _name = 'drm.service.slots'
    _description = 'Register your lift'

    name = fields.Char(string="Title")
    start = fields.Datetime(
        'Start', required=True, help="Start date of an event, without time for full days events")
    stop = fields.Datetime(
        'Stop', required=True, help="Stop date of an event, without time for full days events")
    start_date = fields.Datetime('Start Date', compute='_compute_dates',)
    stop_date = fields.Datetime('End Date', compute='_compute_dates',)
    duration = fields.Float(string="Duration")
    description = fields.Char(string="Description")

    lift_available = fields.Many2one(
        'drm.lift', string="Available Lifts", required=True, readonly=False)
    allday = fields.Boolean('All Day', default=False)

    @api.multi
    @api.depends('allday', 'start', 'stop')
    def _compute_dates(self):
        """ Adapt the value of start_date(time)/stop_date(time) according to start/stop fields and allday. Also, compute
            the duration for not allday meeting ; otherwise the duration is set to zero, since the meeting last all the day.
        """
        for meeting in self:
            if meeting.allday:
                meeting.start_date = meeting.start
                meeting.start_datetime = False
                meeting.stop_date = meeting.stop
                meeting.stop_datetime = False

                meeting.duration = 0.0
            else:
                meeting.start_date = False
                meeting.start_datetime = meeting.start
                meeting.stop_date = False
                meeting.stop_datetime = meeting.stop
