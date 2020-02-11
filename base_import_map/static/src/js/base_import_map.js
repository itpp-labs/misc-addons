odoo.define("base_import_map.map", function(require) {
    "use strict";


    var BaseImport = require("base_import.import");
    var core = require("web.core");

    var _lt = core._lt;
    var _t = core._t;

    BaseImport.DataImport.include({
        init: function() {
            // Assign a new array instead of pushing values to the
            // original one, because otherwise we would change the
            // prototype array, meaning that each time 'init' is called
            // the values are pushed again, resulting in duplicate entries
            this.opts = this.opts.concat([
                {name: "settings", label: _lt("Settings:"), value: ""},
                {name: "save_settings", label: _lt("Save settings:"), value: ""},
                {name: "file_read_hook", label: _lt("File read hook:"), value: ""},
            ]);
            this._super.apply(this, arguments);
        },
        start: function() {
            this.setup_settings_picker();
            this._super();
        },
        setup_settings_picker: function() {
            var self = this;
            self._rpc({
                model: "base_import_map.map",
                method: "search_read",
                args: [[["model", "=", this.res_model]], ["name"]],
            }).then(function(res) {
                var suggestions = [];
                if (res) {
                    res.forEach(function(item) {
                        suggestions.push({id: item.id, text: item.name});
                    });
                } else {
                    suggestions.push({id: "None", text: _t("None")});
                }
                self.$("input.oe_import_settings").select2({
                    width: "160px",
                    query: function(q) {
                        if (q.term) {
                            suggestions.unshift({id: q.term, text: q.term});
                        }
                        q.callback({results: suggestions});
                    },
                    initSelection: function(e, c) {
                        return c({id: "None", text: _t("None")});
                    },
                });
            });
        },
    });
});
