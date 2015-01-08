openerp.mail_wall_widgets = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.mail_wall_widgets.Sidebar = instance.web.Widget.extend({
        template: 'mail_wall_widgets.UserWallSidebar',
        init: function (parent, action) {
            var self = this;
            this._super(parent, action);
            this.deferred = $.Deferred();
            //$(document).off('keydown.klistener');
            this.widget_templates = {
                'mail.wall.widgets.widget': "mail_wall_widgets.Widget"
            }
        },
        events: {
            'click .oe_open_record': function(event){
                var $t = $(event.currentTarget);
                this.do_action({
                    'name': _t('Details'),
                    'type': 'ir.actions.act_window',
                    'res_model': $t.parent().attr('data-model'),
                    'res_id': parseInt($t.attr('data-id')),
                    'target': 'current',
                    'views': [[false, 'form'],[false, 'list']],
                    'domain':  $t.parent().attr('data-domain'),
                })
            },
            'click .oe_open_record_list': function(event){
                var $t = $(event.currentTarget);
                this.do_action({
                    'name': _t('More...'),
                    'type': 'ir.actions.act_window',
                    'res_model': $t.parent().attr('data-model'),
                    'target': 'current',
                    'views': [[false, 'list'],[false, 'form']],
                    'domain':  $t.parent().attr('data-domain'),
                })
            },
            'click .oe_open_record_list_funnel': function(event){
                var $t = $(event.currentTarget);
                this.do_action({
                    'name': _t('More...'),
                    'type': 'ir.actions.act_window',
                    'res_model': $t.parent().attr('data-model'),
                    'target': 'current',
                    'views': [[false, 'list'],[false, 'form']],
                    'domain':  $t.attr('data-domain'),
                })
            },
        },
        start: function() {
            var self = this;
            this._super.apply(this, arguments);
            self.get_widgets_info();
        },
        get_widgets_info: function() {
            var self = this;
            new instance.web.Model('res.users').call('get_serialised_mail_wall_widgets_summary', []).then(function(result) {
                if (result.length === 0) {
                    self.$el.find(".oe_mail_wall_widgets").hide();
                } else {
                    self.$el.find(".oe_mail_wall_widgets").empty();
                    _.each(result, function(item){
                        var $item = $(QWeb.render(self.widget_templates[item.model], {info: item}));
                        self.render_money_fields($item);
                        //self.render_user_avatars($item);
                        self.$el.find('.oe_mail_wall_widgets').append($item);
                    });
                }
            });
        },
        render_money_fields: function(item) {
            var self = this;
            self.dfm = new instance.web.form.DefaultFieldManager(self);
            // Generate a FieldMonetary for each .oe_goal_field_monetary
            item.find(".oe_goal_field_monetary").each(function() {
                var currency_id = parseInt( $(this).attr('data-id'), 10);
                money_field = new instance.web.form.FieldMonetary(self.dfm, {
                    attrs: {
                        modifiers: '{"readonly": true}'
                    }
                });
                money_field.set('currency', currency_id);
                money_field.get_currency_info();
                money_field.set('value', parseInt($(this).text(), 10));
                money_field.replace($(this));
            });
        },
        render_user_avatars: function(item) {
            var self = this;
            item.find(".oe_user_avatar").each(function() {
                var user_id = parseInt( $(this).attr('data-id'), 10);
                var url = instance.session.url('/web/binary/image', {model: 'res.users', field: 'image_small', id: user_id});
                $(this).attr("src", url);
            });
        }
    });

    instance.web.WebClient.include({
        to_kitten: function() {
            this._super();
            new instance.web.Model('mail_wall_widgets.badge').call('check_progress', []);
        }
    });

    instance.mail.Wall.include({
        start: function() {
            this._super();
            var sidebar = new instance.mail_wall_widgets.Sidebar(this);
            sidebar.appendTo($('.oe_mail_wall_aside'));
        },
    });
    
};
