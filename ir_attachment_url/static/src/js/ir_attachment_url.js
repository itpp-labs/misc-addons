odoo.define("ir_attachment_url", function(require) {
    "use strict";
    var core = require("web.core");
    var QWeb = core.qweb;
    var FieldBinaryImage = require("web.field_registry").get("image");
    var _t = core._t;

    FieldBinaryImage.include({
        events: _.extend({}, FieldBinaryImage.prototype.events, {
            "click .o_link_address_button": "on_link_address",
        }),

        init: function(parent, name, record) {
            this._super.apply(this, arguments);
            this.url_clicked = false;
            this.is_url = false;
        },

        on_link_address: function() {
            var self = this;
            this.$el.children(".img-responsive").remove();
            this.$el.children(".input_url").remove();
            this.$el.children(".o_form_image_controls").addClass("media_url_controls");
            this.$el.prepend($(QWeb.render("AttachmentURL", {widget: this})));
            this.$(".input_url input").on("change", function() {
                var input_val = $(this).val();
                self._setValue(input_val);
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

        _render: function() {
            if (!this.is_url_valid(this.value)) {
                return this._super();
            }

            var self = this;
            var attrs = this.attrs;
            var url = this.placeholder;
            if (this.value) {
                url = this.value;
            }
            var $img = $("<img>").attr("src", url);
            $img.css({
                width: this.nodeOptions.size
                    ? this.nodeOptions.size[0]
                    : attrs.img_width || attrs.width,
                height: this.nodeOptions.size
                    ? this.nodeOptions.size[1]
                    : attrs.img_height || attrs.height,
            });
            this.$("> img").remove();
            this.$el.prepend($img);
            $img.on("error", function() {
                self.on_clear();
                $img.attr("src", self.placeholder);
                self.do_warn(_t("Image"), _t("Could not display the selected image."));
            });
        },

        isSet: function() {
            return true;
        },
    });
});
