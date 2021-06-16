// Copyright 2020 Ivan Yelizariev
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
odoo.define('web_website.web_client', function(require) {
"use strict";

    var AbstractWebClient = require('web.AbstractWebClient');
    AbstractWebClient.prototype._onPushState = function (e) {
        var state = $.bbq.getState();
        this.do_push_state(_.extend(e.data.state, {'cids': state.cids, 'wids': state.wids}));
    };
});
