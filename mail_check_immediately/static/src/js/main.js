openerp.mail_check_immediately = function(instance, local) {

    instance.mail.Wall.include({

        init: function(){
            this._super.apply(this, arguments);

            var _this = this;
            var fetchmailTimerId;

            this.events['click a.oe_fetch_new_mails'] = function(){
                _this.get_fetchmail_obj();
            }
        },

        start: function() {
            this._super();
            this.get_last_fetchedmail_time();
            this.get_time_loop()
        },

        get_fetchmail_obj: function(){
            var model = new instance.web.Model('fetch_mail.imm');
            var _this = this;

            model.call('run_fetchmail_manually', {context: new instance.web.CompoundContext()}).then(function(){
                _this.get_last_fetchedmail_time()
            })
        },

        get_last_fetchedmail_time: function(){
           var _this = this;
           var model = new instance.web.Model('fetch_mail.imm');

            model.call('get_last_update_time', {context: new instance.web.CompoundContext()}).then(function(res){
                _this.$el.find('span.oe_view_manager_fetch_mail_imm_field').html(res);
                console.log(res)
            })

        },

        get_time_loop: function(){
            var _this = this;
            fetchmailTimerId = setInterval(function(){
                _this.get_last_fetchedmail_time()
            }, 30000);
        },

        destroy: function(){
        clearInterval(fetchmailTimerId);
        this._super.apply(this, arguments);
        }

    });
};
