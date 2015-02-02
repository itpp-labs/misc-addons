openerp.mail_wall_widgets = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.mail_wall_widgets.Sidebar = instance.web.Widget.extend({
        template: 'mail_wall_widgets.UserWallSidebar',
        init: function (parent, action) {
            var self = this;
            this._super(parent, action);
            this.deferred = $.Deferred();
            self.money_df = $.Deferred()
            self.money_df.resolve();
            self.money_cache = {}
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
                    'res_model': $t.parent().parent().attr('data-model'),
                    'res_id': parseInt($t.attr('data-id')),
                    'target': 'current',
                    'views': [[false, 'form'],[false, 'list']],
                    'domain':  $t.parent().parent().attr('data-domain'),
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
            self.dfm = new instance.web.form.DefaultFieldManager(self);
            new instance.web.Model('res.users').call('get_serialised_mail_wall_widgets_summary', []).then(function(result) {
                if (result.length === 0) {
                    self.$el.find(".oe_mail_wall_widgets").hide();
                } else {
                    self.$el.find(".oe_mail_wall_widgets").empty();
                    _.each(result, function(item){
                        var $item = $(QWeb.render(self.widget_templates[item.model], {info: item}));
                        self.render_money_fields($item);
                        self.render_float_fields($item);
                        //self.render_user_avatars($item);
                        self.$el.find('.oe_mail_wall_widgets').append($item);
                    });
                }
            });
        },
        render_money_fields: function(item) {
            var self = this;
            // Generate a FieldMonetary for each .oe_goal_field_monetary
            item.find(".oe_goal_field_monetary").each(function() {
                var currency_id = parseInt( $(this).attr('data-id'), 10);
                var precision = parseFloat( $(this).attr('data-precision') , 10) || 1;
                var digits = [69,0];
                if (precision && precision<1)
                    digits[1] = ($(this).attr('data-precision') || '0.01').slice(2).indexOf('1')+1;
                var money_field = new instance.web.form.FieldMonetary(self.dfm, {
                    attrs: {
                        'modifiers': '{"readonly": true}',
                        'digits': digits
                    }
                });
                money_field.set('currency', currency_id);
                money_field.set('value', parseInt(parseFloat($(this).text(), 10)/precision)*precision);
                money_field.replace($(this));

                self.money_df =
                    self.money_df.then(function(){
                        var callback = function(){
                            money_field.set({'currency_info': self.money_cache[currency_id]})
                        }
                        if (self.money_cache[currency_id]){
                            callback();
                            return;
                        }
                        var req = new instance.web.Model("res.currency").query(["symbol", "position"]).filter([["id", "=", currency_id]]).first()
                        return req.then(function(res){
                                   self.money_cache[currency_id] = res;
                                   callback();
                               })
                    })
            });
        },
        render_float_fields: function(item) {
            var self = this;
            // Generate a FieldMonetary for each .oe_goal_field_monetary
            item.find(".oe_goal_field_float").each(function() {
                var value = $(this).text();
                if (!value)
                    return;
                var precision = parseFloat( $(this).attr('data-precision'), 10) || 1;
                var digits = [69,0];
                if (precision && precision<1)
                    digits[1] = ($(this).attr('data-precision') || '0.01').slice(2).indexOf('1')+1;

                value = instance.web.format_value(parseFloat(value), {type: "float", digits: digits}, '')
                $(this).text(value)
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
