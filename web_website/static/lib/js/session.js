// Copyright 2020 Ivan Yelizariev
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
/* eslint-disable */
odoo.define('web_website.session', function(require) {
"use strict";

    var Session = require('web.Session');
    var utils = require('web.utils');

    Session.prototype.setWebsites = function (main_website_id, website_ids) {
        var hash = $.bbq.getState();
        hash.wids = website_ids.sort(function(a, b) {
            if (a === main_website_id) {
                return -1;
            } else if (b === main_website_id) {
                return 1;
            } else {
                return a - b;
            }
        }).join(',');
        utils.set_cookie('wids', hash.wids || String(main_website_id));
        $.bbq.pushState({'wids': hash.wids}, 0);
        location.reload();
    };

})
