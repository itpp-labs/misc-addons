odoo.define('web_debranding.about', function(require) {
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var UserMenu = require('web.UserMenu')
    UserMenu.include({
        start: function() {
            this.$el.find("[data-menu='about']").parent().remove();
            this._super();
        },
    }); 
});
