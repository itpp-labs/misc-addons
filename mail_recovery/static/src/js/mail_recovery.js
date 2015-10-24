openerp.mail_recovery = function (session) {
    var mail = session.mail;

    mail.ThreadComposeMessage = mail.ThreadComposeMessage.extend({
        bind_events: function () {
            var self = this;
            this.$('textarea').on('focus', self.on_focus_textarea);
            this.$('textarea').on('keyup', self.on_keyup_textarea);
            this._super();
        },
        on_focus_textarea: function(event) {
            var $input = $(event.target);
            if ($input.val() == false) {
                $input.val(window.localStorage['message_storage']);
            }
        },
        on_keyup_textarea: function(event) {
            window.localStorage['message_storage'] = $(event.target).val();
        },
        on_message_post: function (event) {
            window.localStorage['message_storage'] = '';
            return this._super(event);
        },
    });
};