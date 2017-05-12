odoo.define('web_debranding.dashboard', function (require) {
"use strict";

    var dashboard = require('web_settings_dashboard');
    dashboard.Dashboard.include({
        start: function(){
            this.all_dashboards = _.without(this.all_dashboards, 'planner', 'apps', 'share');
            this.$('.o_web_settings_dashboard_apps').parent().remove();
            this.$('.o_web_settings_dashboard_planner').parent().remove();
            this.$('.o_web_settings_dashboard_share').parent().remove();
            return this._super();
        },
    });
});
