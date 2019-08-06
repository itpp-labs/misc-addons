# Copyright (c) 2004-2015 Odoo S.A.
# Copyright 2018-2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class BaseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_attendance_use_pin = fields.Selection([(0, 'Partners do not need to enter their PIN to check in manually in the "Kiosk Mode".'),
                                                 (1, 'Partners must enter their PIN to check in manually in the "Kiosk Mode".')],
                                                string='Partner PIN',
                                                help='Enable or disable partner PIN identification at check in',
                                                implied_group="base_attendance.group_hr_attendance_use_pin")
    shift_autocheckout = fields.Integer('Autocheckout ', help="Maximum Shift Time in Minutes")
    hex_scanner_is_used = fields.Boolean('HEX Scanner', default=False,
                                         help='Some devices scan regular barcodes as hexadecimal. '
                                              'This option decode those types of barcodes')

    @api.multi
    def set_values(self):
        super(BaseConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        for record in self:
            config_parameters.set_param("base_attendance.shift_autocheckout",
                                        record.shift_autocheckout or '0')
            config_parameters.set_param("base_attendance.hex_scanner_is_used", record.hex_scanner_is_used)
        self.checkout_shifts()

    @api.multi
    def get_values(self):
        res = super(BaseConfigSettings, self).get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        res.update(
            shift_autocheckout=int(config_parameters.get_param("base_attendance.shift_autocheckout", default=0)),
            hex_scanner_is_used=config_parameters.get_param("base_attendance.hex_scanner_is_used", default=False),
        )
        return res

    @api.model
    def checkout_shifts(self):
        cron_record = self.env.ref('base_attendance.base_attendance_autocheckout')
        if self.shift_autocheckout == 0:
            cron_record.write({
                'active': False,
            })
        else:
            cron_record.write({
                'active': True,
            })
