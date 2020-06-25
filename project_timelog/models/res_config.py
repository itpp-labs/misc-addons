from odoo import api, fields, models


class TimelogConfigSettings(models.TransientModel):
    _name = "timelog.config.settings"
    _inherit = "res.config.settings"

    time_subtasks = fields.Float(
        string="Set completion time", help="""Set the time when the timer should stop"""
    )
    time_warning_subtasks = fields.Float(
        string="Set warning time",
        help="""Set the time for how long the timer should warn that it will be stopped""",
    )

    normal_time_day = fields.Float(
        string="Set normal day time",
        help="""Setting time standards provided throughout the day""",
    )
    good_time_day = fields.Float(
        string="Set good day time",
        help="""Set in excess of the time allowed for the day""",
    )

    normal_time_week = fields.Float(
        string="Set normal week time",
        help="""Setting time standards provided throughout the week""",
    )
    good_time_week = fields.Float(
        string="Set good week time",
        help="""Set in excess of the time allowed for the week""",
    )
    first_weekday = fields.Selection(
        [("monday", "Monday"), ("sunday", "Sunday")],
        string="Beginning of the Week",
        default="monday",
    )

    @api.model
    def set_values(self):
        ICPSudo = self.env["ir.config_parameter"].sudo()
        ICPSudo.set_param(key="project_timelog.time_subtasks", value=self.time_subtasks)
        ICPSudo.set_param(
            key="project_timelog.time_warning_subtasks",
            value=self.time_warning_subtasks,
        )
        ICPSudo.set_param(
            key="project_timelog.normal_time_day", value=self.normal_time_day
        )
        ICPSudo.set_param(key="project_timelog.good_time_day", value=self.good_time_day)
        ICPSudo.set_param(
            key="project_timelog.normal_time_week", value=self.normal_time_week
        )
        ICPSudo.set_param(
            key="project_timelog.good_time_week", value=self.good_time_week
        )
        ICPSudo.set_param(key="project_timelog.first_weekday", value=self.first_weekday)
        super(TimelogConfigSettings, self).set_values()

    @api.model
    def get_values(self):
        res = super(TimelogConfigSettings, self).get_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        res.update(
            time_subtasks=ICPSudo.get_param("project_timelog.time_subtasks"),
            time_warning_subtasks=ICPSudo.get_param(
                "project_timelog.time_warning_subtasks"
            ),
            normal_time_day=ICPSudo.get_param("project_timelog.normal_time_day"),
            good_time_day=ICPSudo.get_param("project_timelog.good_time_day"),
            normal_time_week=ICPSudo.get_param("project_timelog.normal_time_week"),
            good_time_week=ICPSudo.get_param("project_timelog.good_time_week"),
            first_weekday=ICPSudo.get_param("project_timelog.first_weekday"),
        )
        return res

    @api.model
    def init_timer_parametrs(self):
        icp = self.env["ir.config_parameter"]
        icp.sudo().set_param(key="project_timelog.time_subtasks", value=2)
        icp.sudo().set_param(key="project_timelog.time_warning_subtasks", value=0.33)
        icp.sudo().set_param(key="project_timelog.normal_time_day", value=5)
        icp.sudo().set_param(key="project_timelog.good_time_day", value=6)
        icp.sudo().set_param(key="project_timelog.normal_time_week", value=30)
        icp.sudo().set_param(key="project_timelog.good_time_week", value=40)
        icp.sudo().set_param(key="project_timelog.first_weekday", value="monday")
