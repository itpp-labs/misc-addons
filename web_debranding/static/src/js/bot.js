odoo.define('web_debranding.bot', function (require) {
    "use strict";

    require('web_debranding.dialog');
    var mail_base = require('mail_base.base');
    var session = require('web.session');

    mail_base.MailTools.include({
        make_message: function(data){
            var msg = this._super(data);
            if (msg.author_id === mail_base.ODOOBOT_ID) {
                msg.avatar_src = '/web/binary/company_logo?company_id=' + session.company_id;
                msg.displayed_author = 'Bot';
            }
            return msg;
        }
    });
});
