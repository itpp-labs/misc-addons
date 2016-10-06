# -*- coding: utf-8 -*-
from openerp import models, fields, api


class TimelogConfigSettings(models.TransientModel):
    _name = 'timelog.config.settings'
    _inherit = 'res.config.settings'

    time_subtasks = fields.Float(string='Set completion time', help="""Set the time when the timer should stop""")
    time_warning_subtasks = fields.Float(string='Set warning time', help="""Set the time for how long the timer should warn that it will be stopped""")
    normal_time_day = fields.Float(string='Set normal time', help="""Setting time standards provided throughout the day""")
    good_time_day = fields.Float(string='Set good time', help="""Set in excess of the time allowed for the day""")
    normal_time_week = fields.Float(string='Set normal time', help="""Setting time standards provided throughout the week""")
    good_time_week = fields.Float(string='Set good time', help="""Set in excess of the time allowed for the week""")

    @api.multi
    def set_custom_parameters(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self:
            config_parameters.set_param(key="project_timelog.time_subtasks", value=record.time_subtasks)
            config_parameters.set_param(key="project_timelog.time_warning_subtasks", value=record.time_warning_subtasks)
            config_parameters.set_param(key="project_timelog.normal_time_day", value=record.normal_time_day)
            config_parameters.set_param(key="project_timelog.good_time_day", value=record.good_time_day)
            config_parameters.set_param(key="project_timelog.normal_time_week", value=record.normal_time_week)
            config_parameters.set_param(key="project_timelog.good_time_week", value=record.good_time_week)

    @api.multi
    def get_default_custom_parameters(self, fields=None):
        icp = self.env['ir.config_parameter']
        return {
            'time_subtasks': icp.get_param('project_timelog.time_subtasks'),
            'time_warning_subtasks': icp.get_param('project_timelog.time_warning_subtasks'),
            'normal_time_day': icp.get_param('project_timelog.normal_time_day'),
            'good_time_day': icp.get_param('project_timelog.good_time_day'),
            'normal_time_week': icp.get_param('project_timelog.normal_time_week'),
            'good_time_week': icp.get_param('project_timelog.good_time_week'),
        }

    @api.model
    def init_timer_parametrs(self):
        icp = self.env["ir.config_parameter"]
        icp.set_param(key="project_timelog.time_subtasks", value=2)
        icp.set_param(key="project_timelog.time_warning_subtasks", value=0.33)
        icp.set_param(key="project_timelog.normal_time_day", value=5)
        icp.set_param(key="project_timelog.good_time_day", value=6)
        icp.set_param(key="project_timelog.normal_time_week", value=30)
        icp.set_param(key="project_timelog.good_time_week", value=40)
