# Copyright (c) 2004-2015 Odoo S.A.
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

from odoo.tests.common import TransactionCase


class TestHrAttendance(TransactionCase):
    """Test for presence validity"""

    def setUp(self):
        super(TestHrAttendance, self).setUp()
        self.test_partner_attendance = self.env["res.partner"].search(
            [("name", "=", "Thomas Passot")]
        )

    def test_partner_attendance_state(self):
        # Make sure the attendance of the partner will display correctly
        assert self.test_partner_attendance.attendance_state == "checked_out"
        self.test_partner_attendance.attendance_action_change()
        assert self.test_partner_attendance.attendance_state == "checked_in"
        self.test_partner_attendance.attendance_action_change()
        assert self.test_partner_attendance.attendance_state == "checked_out"
