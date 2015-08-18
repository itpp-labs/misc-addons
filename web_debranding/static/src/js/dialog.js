function web_debranding_dialog(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.web.CrashManager.include({
        init: function () {
            this._super();
            var self = this;
            var model = new openerp.Model("ir.config_parameter");
            self.debranding_new_name = _t('Software');
            var r = model.query(['value'])
                .filter([['key', '=', 'web_debranding.new_name']])
                .limit(1)
                .all().then(function (data) {
                    if (!data.length)
                        return;
                    self.debranding_new_name = data[0].value;
                });
        },
    });

    instance.web.Dialog.include({
        init: function (parent, options, content) {
            if (parent && parent.debranding_new_name){
                options = options || {};
                if (options['title']){
                    var title = options['title'].replace(/Odoo/ig, parent.debranding_new_name);
                    options['title'] = title;
                }
                if (content){
                    if (typeof content == "string") {
                        var content_html = content.replace(/Odoo/ig, parent.debranding_new_name);
                    } else {
                        var content_html = content.html().replace(/Odoo/ig, parent.debranding_new_name);
                    }
                    content.html(content_html);
                }
            }
            this._super(parent, options, content);
        },
    });
};
