odoo.define('base_import_map.map', function (require) {
    "use strict";

    var ControlPanelMixin = require('web.ControlPanelMixin');
    var BaseImport = require('base_import.import');
    var core = require('web.core');
    var Model = require('web.Model');

    var QWeb = core.qweb;
    var _lt = core._lt;
    var _t = core._t;

    BaseImport.DataImport.include({
        init: function() {
            this.opts.push({name: 'settings', label: _lt("Settings:"), value: ''});
            this.opts.push({name: 'save_settings', label: _lt("Save settings:"), value: ''});
            this.opts.push({name: 'file_read_hook', label: _lt("File read hook:"), value: ''});
            this._super.apply(this, arguments);
        },
        start: function() {
            var self = this;
            this.setup_settings_picker();
            this._super();
        },
        setup_settings_picker: function(){
            var self = this;
            var domain = [['model', '=', this.res_model]];
            var model = new Model("base_import_map.map");
            model.call('name_search', {
                args: domain || false,
            }).then(function(res){
                var suggestions = [];
                if (res) {
                    res.forEach(function (item) {
                        suggestions.push({id: item[0], text: _t(item[1])});
                    });
                } else {
                    suggestions.push({id: "None", text: _t("None")});
                }
                self.$('input.oe_import_settings').select2({
                    width: '160px',
                    query: function (q) {
                        if (q.term) {
                            suggestions.unshift({id: q.term, text: q.term});
                        }
                        q.callback({results: suggestions});
                    },
                    initSelection: function (e, c) {
                        return c({id: "None", text: _t("None")});
                    },
                });
            });
        },
    });
});
