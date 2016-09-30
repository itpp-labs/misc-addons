odoo.define('web_debranding.announcement', function (require) {
"use strict";

    require('mail.announcement');
    var WebClient = require('web.WebClient');
    WebClient.include({
        show_announcement_bar: function() {}
    });
});
