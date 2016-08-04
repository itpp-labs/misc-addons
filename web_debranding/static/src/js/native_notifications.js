odoo.define('web_debranding.native_notifications', function (require) {
"use strict";

    require('web_debranding.dialog');
    var MailTools = require('mail_base.base').MailTools;
    var chat_manager = require('mail_base.base').chat_manager;
    var session = require('web.session');
    var Model = require('web.Model');
    var core = require('web.core');

    var _t = core._t;
    var ChatAction = core.action_registry.get('mail.chat.instant_messaging');

    ChatAction.include({
        init: function(parent, action, options) {
            this._super.apply(this, arguments);
            var self = this;
            var model = new Model("ir.config_parameter");
            self.debranding_new_name = _t('Software');
            model.call('get_param', ['web_debranding.new_name', {}])
                .then(function(result){
                    chat_manager.debranding_new_name = result;
                });
        }
    });

    MailTools.include({
        send_native_notification: function (title, content) {
            if (title == 'Permission granted') {
                content = content.replace(/Odoo/ig, chat_manager.debranding_new_name);
            }
            var notification = new Notification(title, {body: content, icon: '/web/binary/company_logo?company_id=' + session.company_id});
            notification.onclick = function (e) {
                window.focus();
                if (this.cancel) {
                    this.cancel();
                } else if (this.close) {
                    this.close();
                }
            };
        }
    });
});