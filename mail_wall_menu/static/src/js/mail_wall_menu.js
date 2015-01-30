openerp.mail_wall_menu = function(instance){
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.mail.Widget.include({
        start: function(){
            if (this.action.params.disable_thread){
                $('.oe_view_manager_body').addClass('dashboard_only');
                var msnry = new Masonry( '.oe_mail_wall_aside', {
                    // options
                    columnWidth: 290,
                    itemSelector: '.oe_goal',
                    transitionDuration: 0
                });
                var update = -10;
                setInterval(function(){
                    update++;
                    if (update > 0 && update % 5 != 0)
                        return;
                    if (update > 0)
                        update = 0;
                    msnry.reloadItems();
                    msnry.layout();
                }, 1000)


                return;
            }
            this._super.apply(this, arguments)
        }
    })
}