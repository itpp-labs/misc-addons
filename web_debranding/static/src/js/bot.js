odoo.define('web_debranding.bot', function (require) {
    "use strict";

    require('web_debranding.dialog');
    var Message = require('mail.model.Message');
    var session = require('web.session');

    Message.include({
        /**
         * Get the name of the author of this message.
         * If Odoobot is the author (default author for transient messages),
         * returns 'Bot'.
         *
         * @override
         * @private
         * @returns {string}
         */
        _getAuthorName: function () {
            if (this._isOdoobotAuthor()) {
                return "Bot";
            }
            return this._super.apply(this, arguments);
        },

        /**
         * Get the relative url of the avatar to display next to the message
         *
         * @override
         * @return {string}
         */
        getAvatarSource: function () {
            var res = this._super.apply(this, arguments);
            if (res === '/mail/static/src/img/odoo_o.png') {
                return '/web/binary/company_logo?company_id=' + session.company_id;
            }
            return res;
        }
    });
});
