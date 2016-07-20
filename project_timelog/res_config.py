# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

class timelog_config_settings(osv.osv_memory):
    _name = 'timelog.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'time_subtasks': fields.float('Install completion time',
            help="""Set the time for timer subtasks"""),
        'time_warning_subtasks': fields.float('Install warning time',
            help="""Set the warning time for timer subtasks"""),

        'normal_time_day': fields.float('Install normal time',
            help="""Set the normal time for timer day"""),
        'good_time_day': fields.float('Install good time',
            help="""Set the good time for timer day"""),

        'normal_time_week': fields.float('Install normal time',
            help="""Set the normal time for timer weel"""),
        'good_time_week': fields.float('Install good time',
            help="""Set the good time for timer week"""),
    }

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