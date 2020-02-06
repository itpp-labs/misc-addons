# Copyright (c) 2004-2015 Odoo S.A.
# Copyright 2018-2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class BaseConfigSettings(models.TransientModel):
    _inherit = "base.config.settings"

    group_attendance_use_pin = fields.Selection(
        [
            (
                0,
                'Partners do not need to enter their PIN to check in manually in the "Kiosk Mode".',
            ),
            (
                1,
                'Partners must enter their PIN to check in manually in the "Kiosk Mode".',
            ),
        ],
        string="Partner PIN",
        help="Enable or disable partner PIN identification at check in",
        implied_group="base_attendance.group_hr_attendance_use_pin",
    )
    shift_autocheckout = fields.Integer(
        "Autocheckout ", help="Maximum Shift Time in Minutes"
    )
    hex_scanner_is_used = fields.Boolean(
        "HEX Scanner",
        default=False,
        help="Some devices scan regular barcodes as hexadecimal. "
        "This option decode those types of barcodes",
    )

    @api.multi
    def set_shift_autocheckout(self):
        self.env["ir.config_parameter"].set_param(
            "base_attendance.shift_autocheckout", self.shift_autocheckout or "0"
        )
        self.checkout_shifts()

    @api.multi
    def get_default_shift_autocheckout(self, fields):
        shift_autocheckout = self.env["ir.config_parameter"].get_param(
            "base_attendance.shift_autocheckout", default=0
        )
        return {"shift_autocheckout": int(shift_autocheckout)}

    @api.model
    def checkout_shifts(self):
        cron_record = self.env.ref("base_attendance.base_attendance_autocheckout")
        if self.shift_autocheckout == 0:
            cron_record.write({"active": False})
        else:
            cron_record.write({"active": True})

    @api.multi
    def set_hex_scanner_is_used(self):
        self.env["ir.config_parameter"].set_param(
            "base_attendance.hex_scanner_is_used", self.hex_scanner_is_used
        )

    @api.multi
    def get_default_hex_scanner_is_used(self, fields):
        hex_scanner_is_used = self.env["ir.config_parameter"].get_param(
            "base_attendance.hex_scanner_is_used", default=False
        )
        return {"hex_scanner_is_used": hex_scanner_is_used}
