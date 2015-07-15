function web_debranding_dialog(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var debranding_new_name = 'Software';

    instance.web.CrashManager.include({
        init: function () {
            this._super();
            var self = this;
            var model = new openerp.Model("ir.config_parameter");
            var r = model.query(['value'])
                .filter([['key', '=', 'web_debranding.new_name']])
                .limit(1)
                .all().then(function (data) {
                    if (!data.length)
                        return;
                    debranding_new_name = data[0].value;
                });
        },
    });

    instance.web.Dialog.include({
        init: function (parent, options, content) {
            var content_html = content.html().replace(/Odoo/ig, debranding_new_name);
            var title = options['title'].replace(/Odoo/ig, debranding_new_name);
            content.html(content_html);
            options['title'] = title;
            this._super(parent, options, content);
        },
    });
};
