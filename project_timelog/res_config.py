# -*- coding: utf-8 -*-
from openerp import models, fields, api


class TimelogConfigSettings(models.Model):
    _name = 'timelog.config.settings'
    _inherit = 'res.config.settings'

    time_subtasks = fields.Float(string='Install completion time', help="""Set the time when the timer should stop""")
    time_warning_subtasks = fields.Float(string='Install warning time', help="""Set the time for how long the timer should warn that it will be stopped""")
    normal_time_day = fields.Float(string='Install normal time', help="""Setting time standards provided throughout the day""")
    good_time_day = fields.Float(string='Install good time', help="""Installation in excess of the time allowed for the day""")
    normal_time_week = fields.Float(string='Install normal time', help="""Setting time standards provided throughout the week""")
    good_time_week = fields.Float(string='Install good time', help="""Installation in excess of the time allowed for the week""")

    def set_custom_parameters(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "project_timelog.time_subtasks", record.time_subtasks, context=context)
            config_parameters.set_param(cr, uid, "project_timelog.time_warning_subtasks", record.time_warning_subtasks, context=context)
            config_parameters.set_param(cr, uid, "project_timelog.normal_time_day", record.normal_time_day, context=context)
            config_parameters.set_param(cr, uid, "project_timelog.good_time_day", record.good_time_day, context=context)
            config_parameters.set_param(cr, uid, "project_timelog.normal_time_week", record.normal_time_week, context=context)
            config_parameters.set_param(cr, uid, "project_timelog.good_time_week", record.good_time_week, context=context)

    def get_default_custom_parameters(self, cr, uid, ids, context=None):
        icp = self.pool.get('ir.config_parameter')
        return {
            'time_subtasks': icp.get_param(cr, uid, 'project_timelog.time_subtasks', default=2, context=context),
            'time_warning_subtasks': icp.get_param(cr, uid, 'project_timelog.time_warning_subtasks', default=0.33, context=context),
            'normal_time_day': icp.get_param(cr, uid, 'project_timelog.normal_time_day', default=5, context=context),
            'good_time_day': icp.get_param(cr, uid, 'project_timelog.good_time_day', default=6, context=context),
            'normal_time_week': icp.get_param(cr, uid, 'project_timelog.normal_time_week', default=30, context=context),
            'good_time_week': icp.get_param(cr, uid, 'project_timelog.good_time_week', default=40, context=context),
        }
