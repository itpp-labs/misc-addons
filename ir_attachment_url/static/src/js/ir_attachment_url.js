odoo.define('ir_attachment_url', function(require) {
    var utils = require('web.utils');
    var core = require('web.core');
    var form_widgets = require('web.form_widgets');
    var session = require('web.session');
    var QWeb = core.qweb;
    var FieldBinaryImage = core.form_widget_registry.get('image');
    var _t = core._t;
    var common = require('web.form_common');
    var Model = require('web.DataModel');

    FieldBinaryImage.include({
        initialize_content: function() {
            var self = this;
            this.url_clicked = false;
            this.is_url = false;
            this.$('.o_link_address_button').click(function() {
                self.on_link_address();
            });
            this._super();
        },
        render_value: function() {
            if (this.url_clicked) {
                this.$el.children(".img-responsive").remove();
                this.$el.children(".input_url").remove();
                this.$el.children(".o_form_image_controls").addClass("media_url_controls");
                this.$el.prepend($(QWeb.render("AttachmentURL", {widget: this})));
                this.$input = $(".input_url input");
            } else {
                this.$el.children(".o_form_image_controls").removeClass("media_url_controls");
                this.$el.children(".input_url").remove();
                this._super();
            }
        },
        store_dom_url_value: function () {
            if (this.$input && this.$input.val()) {
                if (this.is_url_valid()) {
                    this.set_value(this.$input.val());
                } else {
                    this.do_warn(_t('Warning'), _t('URL is invalid.'));
                }
            }
        },
        on_link_address: function() {
            this.is_url = true;
            if (!this.url_clicked) {
                this.url_clicked = true;
                this.on_clear();
            } else if (this.url_clicked) {
                this.url_clicked = false;
                this.render_value();
            }
        },
        commit_value: function () {
            if (this.is_url) {
                this.store_dom_url_value();
                this.is_url = false;
            }
            return this._super();
        },
        is_url_valid: function() {
            if (this.$input.is('input')) {
                var u = new RegExp("^(http[s]?:\\/\\/(www\\.)?|ftp:\\/\\/(www\\.)?|www\\.){1}([0-9A-Za-z-\\.@:%_~#=]+)+((\\.[a-zA-Z]{2,3})+)(/(.)*)?(\\?(.)*)?");
                return u.test(this.$input.val());
            }
            return true;
        },
    });
});
