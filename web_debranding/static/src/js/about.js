openerp.web_debranding.load_about = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    instance.web.UserMenu.include({
        start: function() {
            this.$el.find("[data-menu='about']").parent().remove();
            this._super();
        },
    }); 
};
