/*  Copyright 2016-2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    Copyright 2017 ArtyomLosev <https://github.com/ArtyomLosev>
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define("web_debranding.native_notifications", function(require) {
    "use strict";

    require("web_debranding.base");
    var session = require("web.session");
    var BusService = require("bus.BusService");
    var core = require("web.core");
    var _t = core._t;

    BusService.include({
        sendNotification: function(title, content, callback) {
            if (
                title === _t("Yay, push notifications are enabled!") ||
                title === _t("Permission denied")
            ) {
                content = content.replace(/Odoo/gi, odoo.debranding_new_name);
            }

            if (window.Notification && Notification.permission === "granted") {
                if (this.isMasterTab()) {
                    this._sendNativeNotification(title, content, callback);
                }
            } else {
                this._super(title, content, callback);
            }
        },
        _sendNativeNotification: function(title, content, callback) {
            var notification = new Notification(title, {
                body: content,
                icon: "/web/binary/company_logo?company_id=" + session.company_id,
            });
            notification.onclick = function() {
                window.focus();
                if (this.cancel) {
                    this.cancel();
                } else if (this.close) {
                    this.close();
                }
                if (callback) {
                    // eslint-disable-next-line
                    callback();
                }
            };
        },
    });

    return BusService;
});
