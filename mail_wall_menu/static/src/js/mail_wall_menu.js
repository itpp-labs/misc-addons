openerp.mail_wall_menu = function(instance){
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.mail.Widget.include({
        start: function(){
            if (this.action.params.disable_thread){
                $('.oe_view_manager_body').addClass('dashboard_only');
                return;
            }
            this._super.apply(this, arguments)
        }
    })
}