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
            var self = this;
            var context = {
                'default_message_id': this.id
            }
            var action = {
                name: _t('Relocate Message'),
                type: 'ir.actions.act_window',
                res_model: 'mail_move_message.wizard',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: context,
            };

            self.do_action(action, {
                'on_close': function(){
                    self.check_for_rerender();
                }
            });
        }
    })

    mail.MessageCommon.include({
        init: function (parent, datasets, options) {
            this._super(parent, datasets, options);
            this.is_moved = datasets.is_moved ||  false;
        }
    })

    session.web.form.WidgetButton.include({
        on_click: function() {
            if(this.node.attrs.special == 'quick_create'){
                var self = this;
                var related_field = this.field_manager.fields[this.node.attrs['field']];
                var context_built = $.Deferred();
                if(this.node.attrs.use_for_mail_move_message) {
                    var model = new session.web.Model(this.view.dataset.model);
                    var partner_id = self.field_manager.fields['partner_id'].get_value();
                    var message_name_from = self.field_manager.fields['message_name_from'].get_value();
                    var message_email_from = self.field_manager.fields['message_email_from'].get_value();
                    context_built = model.call('create_partner', [self.view.dataset.context.default_message_id,
                        related_field.field.relation, partner_id, message_name_from, message_email_from]);
                }
                else {
                    context_built.resolve(this.build_context());
                }
                $.when(context_built).pipe(function (context) {
                    if(self.node.attrs.use_for_mail_move_message) {
                        self.field_manager.fields['partner_id'].set_value(context['partner_id']);
                    }
                    var pop = new session.web.form.FormOpenPopup(this);
                    pop.show_element(
                        related_field.field.relation,
                        false,
                        context,
                        {
                            title: _t("Create new record"),
                        }
                    );
                    pop.on('closed', self, function () {
                        self.force_disabled = false;
                        self.check_disable();
                    });
                    pop.on('create_completed', self, function(id) {
                        related_field.set_value(id);
                    });
                });
            }
            else {
                this._super.apply(this, arguments);
            }
        },
    });

}