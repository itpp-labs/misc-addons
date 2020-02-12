/* eslint complexity: "off"*/
odoo.define("media_form_widget", function(require) {
    "use strict";
    var core = require("web.core");
    var KanbanRecord = require("web_kanban.Record");
    var session = require("web.session");
    var QWeb = core.qweb;
    var FieldBinaryImage = core.form_widget_registry.get("image");
    var _t = core._t;

    FieldBinaryImage.include({
        initialize_content: function() {
            this.media_type = this.view.datarecord.media_type;
            this.media_video_ID = this.view.datarecord.media_video_ID;
            this.media_video_service = this.view.datarecord.media_video_service;
            this.media = this.node.attrs.media;
            this._super();
        },
        render_value: function() {
            this.media_id = this.view.datarecord.id;
            var application_mimetype = false;
            if (this.media_type && this.media_type.split("/")[0] === "application") {
                application_mimetype = true;
            }
            if (
                this.media &&
                (this.media_type === "video/url" ||
                    application_mimetype ||
                    this.media_type === "application/msword")
            ) {
                var url = "/web/static/src/img/mimetypes/document.png";
                if (this.media_type === "video/url") {
                    url = "/web/static/src/img/mimetypes/video.png";
                    if (this.media_video_service === "youtube") {
                        url = "/web_preview/static/src/img/youtube.png";
                    } else if (this.media_video_service === "vimeo") {
                        url = "/web_preview/static/src/img/vimeo.png";
                    }
                } else if (this.media_type === "application/pdf") {
                    url = "/web_preview/static/src/img/pdf.png";
                    this.pdf_url = this.get_media_url("/web/pdf");
                } else if (this.media_type === "application/msword") {
                    url = "/web_preview/static/src/img/doc.png";
                    this.msword_url = this.get_media_url("/web/doc");
                } else if (
                    this.media_type ===
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ) {
                    url = "/web_preview/static/src/img/xlsx.png";
                    this.xlsx_url = this.get_media_url("/web/xlsx");
                } else if (this.media_type === "application/vnd.ms-excel") {
                    url = "/web_preview/static/src/img/xls.png";
                    this.xls_url = this.get_media_url("/web/xls");
                } else if (
                    this.media_type ===
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ) {
                    url = "/web_preview/static/src/img/docx.png";
                    this.docx_url = this.get_media_url("/web/docx");
                } else {
                    this.do_warn(
                        _t("Document"),
                        _t("Could not display the selected document.")
                    );
                }
                var $media = $(
                    QWeb.render("FieldBinaryImage-img", {widget: this, url: url})
                );
                this.$("> img").remove();
                this.$("> a img").remove();
                this.$el.prepend($media);
            } else {
                if (this.media_type && this.media_type.split("/")[0] === "image") {
                    this.media_type = "image";
                }
                this._super();
            }
        },
        on_file_uploaded_and_valid: function(size, name, content_type, file_base64) {
            this.media_type = content_type;
            this._super(size, name, content_type, file_base64);
        },
        get_media_url: function(request) {
            return session.url(request, {
                model: this.view.dataset.model,
                id: JSON.stringify(this.view.datarecord.id),
                field: this.name,
                filename: this.view.datarecord.display_name,
                unique: (this.view.datarecord.__last_update || "").replace(
                    /[^0-9]/g,
                    ""
                ),
            });
        },
    });

    KanbanRecord.include({
        kanban_image: function(model, field, id, cache, options) {
            if (
                this.values.media_type &&
                this.values.media_type.value === "application/pdf"
            ) {
                return "/web_preview/static/src/img/pdf.png";
            } else if (
                this.values.media_type &&
                this.values.media_type.value === "application/msword"
            ) {
                return "/web_preview/static/src/img/doc.png";
            } else if (
                this.values.media_type &&
                this.values.media_type.value ===
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ) {
                return "/web_preview/static/src/img/docx.png";
            } else if (
                this.values.media_type &&
                this.values.media_type.value === "application/vnd.ms-excel"
            ) {
                return "/web_preview/static/src/img/xls.png";
            } else if (
                this.values.media_type &&
                this.values.media_type.value ===
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ) {
                return "/web_preview/static/src/img/xlsx.png";
            } else if (
                this.values.media_video_service &&
                this.values.media_video_service.value
            ) {
                var video = this.values.media_video_service.value;
                if (video === "youtube") {
                    return "/web_preview/static/src/img/youtube.png";
                }
                if (video === "vimeo") {
                    return "/web_preview/static/src/img/vimeo.png";
                }
            }
            return this._super(model, field, id, cache, options);
        },
    });
});
