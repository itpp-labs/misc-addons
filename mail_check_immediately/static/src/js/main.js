openerp.mail_check_immediately = function(instance, local) {

    instance.mail.Wall.include({

        init: function(){
            this._super.apply(this, arguments);

            var _this = this;

            this.imm_model = new instance.web.Model('fetch_mail.imm');
            this.events['click a.oe_fetch_new_mails'] = function(){
                _this.run_fetchmail_manually();
            }
        },

        start: function() {
            var _this = this;


            this._super();

            this.get_last_fetched_time();

            this.get_time_loop = setInterval(function(){
                _this.get_last_fetched_time()
            }, 30000);

        },

        run_fetchmail_manually: function(){
            var _this = this;

            this.imm_model.call('run_fetchmail_manually', {context: new instance.web.CompoundContext()}).then(function(){
                _this.get_last_fetched_time()
            })
        },

        get_last_fetched_time: function(){
            var _this = this;
            this.imm_model.call('get_last_update_time', {context: new instance.web.CompoundContext()}).then(function(res){
                var value;
                if (res)
                    value = $.timeago(res);
                value = value || 'undefined';
                _this.$el.find('span.oe_view_manager_fetch_mail_imm_field').html(value);
            })
        },

        destroy: function(){
            clearInterval(this.get_time_loop);
        this._super.apply(this, arguments);
        }

    });
};
