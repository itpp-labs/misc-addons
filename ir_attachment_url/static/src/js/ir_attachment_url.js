odoo.define("ir_attachment_url", function(require) {
    "use strict";
    var core = require("web.core");
    var QWeb = core.qweb;
    var FieldBinaryImage = require("web.basic_fields").FieldBinaryImage;

    FieldBinaryImage.include({
        events: _.extend({}, FieldBinaryImage.prototype.events, {
            "click .o_link_address_button": "on_link_address",
        }),

        on_link_address: function() {
            var self = this;
            this.$el.children(".img-responsive").remove();
            this.$el.children(".input_url").remove();
            this.$el.children(".o_form_image_controls").addClass("media_url_controls");
            this.$el.prepend($(QWeb.render("AttachmentURL", {widget: this})));
            this.$(".input_url input").on("change", function() {
                var input_val = $(this).val();
                if (self.is_url_valid(input_val)) {
                    $.get("/web/convert_url_to_base64", {
                        url: input_val,
                    }).then(function(result) {
                        self._setValue(result);
                    });
                }
            });
        },

        is_url_valid: function(value) {
            if (value || (this.$input && this.$input.is("input"))) {
                var u = new RegExp(
                    "^(http[s]?:\\/\\/(www\\.)?|ftp:\\/\\/(www\\.)?|www\\.){1}([0-9A-Za-z-\\.@:%_~#=]+)+((\\.[a-zA-Z]{2,3})+)(/(.)*)?(\\?(.)*)?"
                );
                return u.test(value || this.$input.val());
            }
            return true;
        },
    });
});
