# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License MIT (https://opensource.org/licenses/MIT).

from datetime import datetime, timedelta

from odoo import fields, http
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo.addons.odoo_backup_sh.controllers.main import BackupController


class NewBackupController(BackupController):
    @http.route()
    def fetch_dashboard_data(self):
        dashboard_data = super(NewBackupController, self).fetch_dashboard_data()
        date_month_before = datetime.now().date() - timedelta(days=29)
        date_list = [date_month_before + timedelta(days=x) for x in range(30)]
        last_month_domain = [
            ("date", ">=", datetime.strftime(date_list[0], DEFAULT_SERVER_DATE_FORMAT))
        ]
        values = (
            request.env["odoo_backup_sh.remote_storage"]
            .search(last_month_domain)
            .sorted(key="date")
        )
        dropbox_usage_values = {r.date: r.dropbox_used_remote_storage for r in values}
        for date in date_list:
            if date not in dropbox_usage_values:
                if date_list.index(date) == 0:
                    dropbox_usage_values[date] = 0
                else:
                    dropbox_usage_values[date] = dropbox_usage_values.get(
                        date_list[date_list.index(date) - 1], 0
                    )

        dashboard_data["services_storage_usage_graph_values"].update(
            {
                "dropbox": [
                    {
                        "key": "Remote Dropbox Storage Usage",
                        "values": [
                            {
                                0: fields.Date.to_string(day),
                                1: dropbox_usage_values[day],
                            }
                            for day in date_list
                        ],
                    }
                ]
            }
        )
        return dashboard_data
