odoo.define('web_debranding.bot', function (require) {
    "use strict";

    require('web_debranding.dialog');
    var chat_manager = require('mail.chat_manager');
    var session = require('web.session');
    var ODOOBOT_ID = "ODOOBOT";

    var make_message_super = chat_manager.make_message;
    chat_manager.make_message = function(data){
            var msg = make_message_super(data);
            if (msg.author_id === ODOOBOT_ID) {
                msg.avatar_src = '/web/binary/company_logo?company_id=' + session.company_id;
                msg.displayed_author = 'Bot';
            }
            return msg;
    };
});
