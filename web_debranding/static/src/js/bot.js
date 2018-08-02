odoo.define('web_debranding.bot', function (require) {
    "use strict";

    require('web_debranding.dialog');
    var Message = require('mail.model.Message');
    var session = require('web.session');

    Message.include({
        _getAuthorName: function () {
            if (this._isOdoobotAuthor()) {
                return "Bot";
            }
            return this._super.apply(this, arguments);
        },

        getAvatarSource: function () {
            var res = this._super.apply(this, arguments);
            if (res === '/mail/static/src/img/odoo_o.png') {
                return '/web/binary/company_logo?company_id=' + session.company_id;
            }
            return res;
        }
    });
});
