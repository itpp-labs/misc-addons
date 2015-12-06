odoo.define('web_debranding.dashboard', function (require) {
"use strict";

    var dashboard = require('web_settings_dashboard');
    dashboard.Dashboard.include({
        start: function(){
            return this.load(['invitations'])
        },
    });
});
