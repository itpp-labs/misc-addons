odoo.define('web_debranding.title', function(require) {
    var core = require('web.core');
    var session = require('web.session');
    var QWeb = core.qweb;
    var Model = require('web.Model');

    var _t = core._t;
    var WebClient = require('web.WebClient');
    WebClient.include({
    init: function(parent, client_options) {
        this._super(parent, client_options);
        this.set('title_part', {"zopenerp": ''});
        this.update_title_part();
    },
    show_application: function(){
        this._super.apply(this, arguments);
        this.update_title_part();
    },
    update_title_part: function(){
        if (!session.db)
            return;
        var self = this;
        var model = new Model("ir.config_parameter");

        var r = model.query(['value'])
             .filter([['key', '=', 'web_debranding.new_title']])
             .limit(1)
             .all().then(function (data) {
                 if (!data.length)
                     return;
                 title_part = data[0].value;
                 title_part = title_part.trim();
                 self.set('title_part', {"zopenerp": title_part});
                 });
    },
 }); 
});
