# -*- coding: utf-8 -*-
import datetime
import time
from openerp import models, fields, api, SUPERUSER_ID
from openerp import http

class ProjectTimeLog(models.Model):
    _name = "project.timelog"
    _description = "project timelog"

    work_id  = fields.Many2one("project.task.work", "Task", required=True)
    start_datetime = fields.Datetime(string="Start date", default=datetime.datetime.now())
    end_datetime = fields.Datetime(string="End date", default=None)
    duration = fields.Char(string="Duration", compute='_compute_duration', store=True)
    user_id = fields.Many2one("res.users", string="User name")

    @api.one
    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        if self.end_datetime == None:
            self.duration = None
        else:
            resultat = self.end_datetime - self.start_datetime
            if (resultat.days == 1):
                out = str(resultat).replace(" day, ", ":")
            elif (resultat.days > 1):
                out = str(resultat).replace(" days, ", ":")
            else:
                out = "0:" + str(resultat)
            outAr = out.split(':')
            outAr = ["%02d" % (int(float(x))) for x in outAr]
            self.duration = ":".join(outAr)
