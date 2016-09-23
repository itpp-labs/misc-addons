odoo.define('web_debranding.base', function(require) {
    var Model = require('web.Model');
    var WebClient = require('web.WebClient');
    var core = require('web.core');

    var _t = core._t;

    WebClient.include({
        init: function(parent, action, options) {
            this._super.apply(this, arguments);
            var self = this;
            var model = new Model("ir.config_parameter");
            odoo.debranding_new_name = _t('Software');
            model.call('get_param', ['web_debranding.new_name', {}])
                .then(function(result){
                    odoo.debranding_new_name = result || '';
                });
        }
    });

})
