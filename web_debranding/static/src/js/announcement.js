odoo.define('mail.announcement', function (require) {
"use strict";

    require('mail.announcement');
    var WebClient = require('web.WebClient');
    WebClient.include({
        show_annoucement_bar: function() {}
    });
};
