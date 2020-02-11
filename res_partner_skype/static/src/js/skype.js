odoo.define("res_partner_skype.widget", function(require) {
    "use strict";

    var core = require("web.core");
    var FieldChar = core.form_widget_registry.get("char");

    var FieldSkype = FieldChar.extend({
        template: "FieldSkype",
        prefix: "skype",
        init: function() {
            this._super.apply(this, arguments);
            this.clickable = true;
        },

        render_value: function() {
            this._super();
            if (this.get("effective_readonly") && this.clickable) {
                this.$el.attr(
                    "href",
                    this.prefix +
                        ":" +
                        this.get("value") +
                        "?" +
                        (this.options.type || "call")
                );
            }
        },
    });

    core.form_widget_registry.add("skype", FieldSkype);
});
