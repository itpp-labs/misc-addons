openerp.web_debranding.load_title = function(instance) {
 var QWeb = instance.web.qweb;
 var _t = instance.web._t;
 instance.web.WebClient.include({
    init: function(parent, client_options) {
        this._super(parent, client_options);
        this.set('title_part', {"zopenerp": ''});
        this.get_title_part();
    },
    get_title_part: function(){
        if (!openerp.session.db)
            return;
        var self = this;
        var model = new openerp.Model("ir.config_parameter");

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
};
