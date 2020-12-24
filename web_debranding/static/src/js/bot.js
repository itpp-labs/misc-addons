/*  Copyright 2016-2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    License MIT (https://opensource.org/licenses/MIT). */
odoo.define("web_debranding.bot", function (require) {
    "use strict";

    require("web_debranding.dialog");
    var chat_manager = require("mail.chat_manager");
    var session = require("web.session");
    var ODOOBOT_ID = "ODOOBOT";

    chat_manager._make_message_debranding_bot_super = chat_manager.make_message;
    chat_manager.make_message = function (data) {
        var msg = this._make_message_debranding_bot_super(data);
        if (msg.author_id === ODOOBOT_ID) {
            msg.avatar_src =
                "/web/binary/company_logo?company_id=" + session.company_id;
            msg.displayed_author = "Bot";
        }
        return msg;
    };
});
