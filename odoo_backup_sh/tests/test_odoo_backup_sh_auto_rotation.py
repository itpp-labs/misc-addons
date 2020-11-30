# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# Copyright 2020 Denis Mudarisov <https://github.com/trojikman>
# License MIT (https://opensource.org/licenses/MIT).

from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestOdooBackupSh(TransactionCase):
    def test_compute_auto_rotation_backup_dts(self):
        dt_start = datetime(2018, 10, 1, 12, 0, 0, 0)
        backup_dts = [
            dt_start,  # 0, it's a monday, week 40, month 10
            dt_start - timedelta(hours=3),  # 1
            dt_start - timedelta(days=1),  # 2, week 39, month 9
            dt_start - timedelta(days=3),  # 3
            dt_start - timedelta(days=10),  # 4, week 38
            dt_start - timedelta(days=21),  # 5
            dt_start - timedelta(days=42),  # 6, month 8
            dt_start - timedelta(days=367),  # 7
            dt_start - timedelta(days=734),  # 8
        ]
        self.assertEqual(
            self.env["odoo_backup_sh.config"].compute_auto_rotation_backup_dts(
                backup_dts, hourly=4
            ),
            [dt for dt in backup_dts if backup_dts.index(dt) in [0, 1, 2, 3]],
        )
        self.assertEqual(
            self.env["odoo_backup_sh.config"].compute_auto_rotation_backup_dts(
                backup_dts, daily=3
            ),
            [dt for dt in backup_dts if backup_dts.index(dt) in [0, 2, 3]],
        )
        self.assertEqual(
            self.env["odoo_backup_sh.config"].compute_auto_rotation_backup_dts(
                backup_dts, weekly=10
            ),
            [dt for dt in backup_dts if backup_dts.index(dt) in [0, 2, 4, 5, 6, 7, 8]],
        )
        self.assertEqual(
            self.env["odoo_backup_sh.config"].compute_auto_rotation_backup_dts(
                backup_dts, monthly=3
            ),
            [dt for dt in backup_dts if backup_dts.index(dt) in [0, 2, 6]],
        )
        self.assertEqual(
            self.env["odoo_backup_sh.config"].compute_auto_rotation_backup_dts(
                backup_dts, yearly=2
            ),
            [dt for dt in backup_dts if backup_dts.index(dt) in [0, 7]],
        )
        self.assertEqual(
            self.env["odoo_backup_sh.config"].compute_auto_rotation_backup_dts(
                backup_dts, hourly=2, daily=2, weekly=3
            ),
            [dt for dt in backup_dts if backup_dts.index(dt) in [0, 1, 2, 4]],
        )
        dt_start = datetime(2018, 10, 1, 12, 0, 0, 0)
        backup_dts = [
            dt_start - timedelta(minutes=1),
            dt_start - timedelta(minutes=3),
            dt_start - timedelta(minutes=6),
            dt_start - timedelta(minutes=9),
        ]
        self.assertEqual(
            self.env["odoo_backup_sh.config"].compute_auto_rotation_backup_dts(
                backup_dts, hourly=1000
            ),
            [backup_dts[i] for i in [0]],
        )
