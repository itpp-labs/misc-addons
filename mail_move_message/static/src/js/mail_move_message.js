openerp.mail_move_message = function (session) {
    var _t = session.web._t,
       _lt = session.web._lt;

    var mail = session.mail;

    mail.ThreadMessage.include({
        bind_events: function(){
            this._super.apply(this, arguments);
            this.$('.oe_move').on('click', this.on_move_message)
        },
        on_move_message: function(event){
            var context = {
                'default_message_id': this.id
            }
            var action = {
                type: 'ir.actions.act_window',
                res_model: 'mail_move_message.wizard',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: context,
            };

            this.do_action(action);
        }
    })

    mail.MessageCommon.include({
        init: function (parent, datasets, options) {
            this._super(parent, datasets, options);
            this.is_moved = datasets.is_moved ||  false;
        }
    })
}