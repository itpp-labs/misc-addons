odoo.define('media_form_widget', function(require) {
    var utils = require('web.utils');
    var core = require('web.core');
    var form_widgets = require('web.form_widgets');
    var session = require('web.session');
    var QWeb = core.qweb;
    var FieldBinaryFile = core.form_widget_registry.get('binary');
    var _t = core._t;
    var common = require('web.form_common');
    var Model = require('web.DataModel');


    var MediaFormViewer = FieldBinaryFile.extend({
        template: 'MediaFormViewer',
        placeholder: "/web/static/src/img/mimetypes/document.png",
        initialize_content: function() {
            this.media_type = this.view.datarecord.media_type;
            this._super();
        },
        render_value: function() {
            var url = this.placeholder;
            var href_url = false;
            if (this.media_type) {
                this.type = this.media_type.split('/');
                if (this.type[0] == "image") {
                    if(this.get('value')) {
                        if(!utils.is_bin_size(this.get('value'))) {
                            url = 'data:image/png;base64,' + this.get('value');
                        } else {
                            url = session.url('/web/image', {
                                model: this.view.dataset.model,
                                id: JSON.stringify(this.view.datarecord.id || null),
                                field: (this.options.preview_image)? this.options.preview_image : this.name,
                                unique: (this.view.datarecord.__last_update || '').replace(/[^0-9]/g, ''),
                            });
                        }
                    }
                } else if (this.type[0] == "application"){
                    if (this.type[1] == "pdf") {
                        url = "/web/static/src/img/mimetypes/pdf.png";
                        href_url = session.url('/web/pdf', {
                            model: this.view.dataset.model,
                            id: JSON.stringify(this.view.datarecord.id),
                            field: this.name,
                            filename: this.view.datarecord.display_name,
                            unique: (this.view.datarecord.__last_update || '').replace(/[^0-9]/g, ''),
                        });
                    } else {
                        this.do_warn(_t("Document"), _t("Could not display the selected document."));
                    }
                } else {
                    this.do_warn(_t("Document"), _t("Could not display the selected document."));
                }
            }

            this.media_id = this.view.datarecord.id;
            var media = $(QWeb.render("MediaFormViewer-img", {widget: this, url: url, href_url: href_url}));

            var self = this;
            media.click(function(e) {
                if(self.view.get("actual_mode") == "view") {
                    var $button = $(".o_form_button_edit");
                    $button.openerpBounce();
                    e.stopPropagation();
                }
            });
            this.$('> img').remove();
            this.$('> a img').remove();
            if (self.options.size) {
                media.css("width", "" + self.options.size[0] + "px");
                media.css("height", "" + self.options.size[1] + "px");
            }
            this.$el.prepend(media);
            media.on('error', function() {
                self.on_clear();
                media.attr('src', self.placeholder);
                self.do_warn(_t("Image"), _t("Could not display the selected document."));
            });
        },
        set_value: function(value_) {
            var changed = value_ !== this.get_value();
            this._super.apply(this, arguments);
            if (!changed){
                this.trigger("change:value", this, {
                    oldValue: value_,
                    newValue: value_
                });
            }
        },
        is_false: function() {
            return false;
        },
        set_dimensions: function(height, width) {
            this.$el.css({
                maxWidth: width,
                minHeight: height,
            });
        },
        on_clear: function() {
            this.media_type = false;
            this._super();
        },
        on_file_uploaded_and_valid: function(size, name, content_type, file_base64) {
            this.media_type = content_type;
            this._super(size, name, content_type, file_base64);
        },
    });
    core.form_widget_registry.add('media', MediaFormViewer);
});
