// Copyright 2019 Dinar Gabbasov Krotov <https://it-projects.info/team/GabbasovDinar>
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

odoo.define("odoo_backup_sh_dropbox.dashboard", function(require) {
    "use strict";

    var Dashboard = require("odoo_backup_sh.dashboard");

    Dashboard.include({
        click_group_buttons: function(e) {
            var $el = $(e.target);
            var service = $el.data("service");
            if ($el.data("service") === "dropbox") {
                this.set_active_button($el);
                this.set_service(service);
                this.render_remote_storage_usage_graph(
                    this.services_storage_usage_graph_values[service]
                );
            } else {
                this._super(e);
            }
        },
        renderElement: function() {
            this._super();
            this.$(".kanban_group_buttons").removeClass("o_hidden");
        },
        render_backup_config_cards: function() {
            this._super();
            this.$(".backup_storage_service_title").removeClass("o_hidden");
        },
    });

    return Dashboard;
});
