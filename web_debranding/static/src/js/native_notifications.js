/*  Copyright 2016-2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    Copyright 2017 ArtyomLosev <https://github.com/ArtyomLosev>
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define("web_debranding.native_notifications", function(require) {
    "use strict";

    require("web_debranding.base");
    var session = require("web.session");
    var utils = require("mail.utils");
    var bus = require("bus.bus").bus;


    var _send_native_notification = function(title, content) {
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
        };
    };

    var send_notification_super = utils.send_notification;
    utils.send_notification = function(widget, title, content) {
        if (title === "Permission granted" || title === "Permission denied") {
            content = content.replace(/Odoo/gi, odoo.debranding_new_name);
        }
        if (Notification && Notification.permission === "granted") {
            if (bus.is_master) {
                _send_native_notification(title, content);
            }
        } else {
            send_notification_super(widget, title, content);
        }
    };
});
