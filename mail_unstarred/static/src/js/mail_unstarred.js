openerp.mail_unstarred = function(session) {

    var mail = session.mail;

    mail.ThreadMessage.include({

        on_star: function (event) {
            event.stopPropagation();
            var self=this;
            var button = self.$('.oe_star:first');

            this.ds_message.call('set_message_starred', [[self.id], !self.is_favorite, true])
                .then(function (star) {
                    self.is_favorite=star;
                    if (self.is_favorite) {
                        button.addClass('oe_starred');
                    } else {
                        button.removeClass('oe_starred');
                    }

                    if (self.options.view_inbox && self.is_favorite) {
                        self.on_message_read_unread(true);
                    }
                    else {
                        self.check_for_rerender();
                    }
                    if (self.options.view_todo && !self.is_favorite) {
                        self.on_message_read_unread(true);
                    }
                });
            return false;
        },

    });

    mail.Widget.include({

        init: function (parent, action) {
            this._super(parent, action);
            this.action.params.view_todo = this.action.context.view_todo || false;
        },

    });
}