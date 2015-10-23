openerp.mail_recovery = function (session) {
    var mail = session.mail;

    mail.ThreadComposeMessage = mail.ThreadComposeMessage.extend({
        init: function (parent, datasets, options) {
            console.log("privet");
            return this._super(parent, datasets, options);
        },
        bind_events: function () {
            var self = this;
            this.$('textarea').on('focus', self.on_focus_textarea);
            this.$('textarea').on('change', self.on_change_textarea);
            this._super();
        },
        on_focus_textarea: function(event) {
            $(event.target).val(window.localStorage['message_storage']);
        },
        on_change_textarea: function(event) {
            window.localStorage['message_storage'] = $(event.target).val();
        },
        on_message_post: function (event) {
            window.localStorage['message_storage'] = '';
            return this._super(event);
        },
    });
};