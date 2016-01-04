odoo.define('access_apps.dashboard', function (require) {
"use strict";

    var dashboard = require('web_settings_dashboard');

    dashboard.Dashboard.include({
        load_apps: function(data){
            if(data['has_access_to_apps']) {
                return this._super(data);
            } else {
                this.$('.o_web_settings_dashboard_apps').parent().remove();
            }
        },
   });
});
