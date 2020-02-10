/*  Copyright 2016-2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('web_debranding.bot', function (require) {
    "use strict";

    require('web_debranding.dialog');
    var Message = require('mail.model.Message');
    var session = require('web.session');
    var MailBotService = require('mail_bot.MailBotService');
    var core = require('web.core');
    var _t = core._t;

    Message.include({
        _getAuthorName: function () {
            if (this._isOdoobotAuthor()) {
                return "Bot";
            }
            return this._super.apply(this, arguments);
        },
        getAvatarSource: function () {
            if (this._isOdoobotAuthor()) {
                return '/web/binary/company_logo?company_id=' + session.company_id;
            }
            return this._super.apply(this, arguments);
        }
    });

    MailBotService.include({
        getPreviews: function (filter) {
            var previews = this._super.apply(this, arguments);
            previews.map(function(preview) {
                if (preview.title === _t("OdooBot has a request")) {
                    preview.title = _t("Bot has a request");
                }
                if (preview.imageSRC === "/mail/static/src/img/odoobot.png") {
                    preview.imageSRC = '/web/binary/company_logo?company_id=' + session.company_id;
                }
                return preview;
            });
            return previews;
        },
    });

});
