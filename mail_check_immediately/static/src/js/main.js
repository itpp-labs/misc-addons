openerp.mail_check_immediately = function(instance, local) {

    instance.mail.Wall.include({
        start: function() {
            var _this = this;

            this._super();
            this.get_last_update_time();
            this.get_time_loop()
        },

        events: {
          'click a.oe_fetch_new_mails': function(){
              this.get_fetchmail_obj();
          }
        },

        get_fetchmail_obj: function(){
            var model = new instance.web.Model('fetch_mail.imm');
            var _this = this;

            model.call('run_fetchmail_manually', {context: new instance.web.CompoundContext()}).then(function(){
                _this.get_last_update_time()
            })
        },

        get_last_update_time: function(){
           var _this = this;
           var fetchmail = new instance.web.Model('fetchmail.server');

           fetchmail.query(['run_time']).all().then(function(res){
                    _this.$el.find('span.oe_view_manager_fetch_mail_imm_field').html(res[0].run_time);
                })
        },

        get_time_loop: function(){
            var _this = this;
            setInterval(function(){
                _this.get_last_update_time()
            }, 30000)

        }
    });
};