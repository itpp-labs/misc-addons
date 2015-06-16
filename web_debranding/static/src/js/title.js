(function() {

var instance = openerp;
openerp.web.chrome = {};

var QWeb = instance.web.qweb,
    _t = instance.web._t;

 instance.web.WebClient.include({
    init: function(parent, client_options) {
        this._super(parent, client_options);
        this.get_title_part();
        this.set('title_part', {"zopenerp": ''});
    },
    get_title_part: function(){
        var self = this;
        var model = new openerp.Model("ir.config_parameter");

        var r = model.query(['value'])
             .filter([['key', '=', 'web_debranding.new_title']])
             .limit(1)
             .all().then(function (data) {
                 title_part = data[0].value;
                 title_part = title_part.trim();
                 self.set('title_part', {"zopenerp": title_part});
                 });
    },
 }); 

})();
