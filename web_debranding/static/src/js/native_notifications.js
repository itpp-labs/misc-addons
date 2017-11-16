odoo.define('web_debranding.native_notifications', function (require) {
    "use strict";

    require('web_debranding.base');
    var session = require('web.session');
    var core = require('web.core');
    var utils = require('mail.utils');
    var bus = require('bus.bus').bus;

    var _t = core._t;

    var _send_native_notification = function (title, content) {
        var notification = new Notification(title, {body: content, icon: '/web/binary/company_logo?company_id=' + session.company_id});
        notification.onclick = function () {
            window.focus();
            if (this.cancel) {
                this.cancel();
            } else if (this.close) {
                this.close();
            }
        };
    };

    var send_notification_super = utils.send_notification;
    utils.send_notification = function (widget, title, content) {
        if (title === 'Permission granted' || title === 'Permission denied') {
            content = content.replace(/Odoo/ig, odoo.debranding_new_name);
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
