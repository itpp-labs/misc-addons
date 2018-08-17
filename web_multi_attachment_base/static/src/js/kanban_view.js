/*  Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
    Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).*/
odoo.define('kanban_view', function (require) {
    "use strict";

    var core = require('web.core');
    var KanbanView = require('web.KanbanView');
    var KanbanRenderer = require('web.KanbanRenderer');
    var AbstractField = require('web.AbstractField');
    var relational_fields = require('web.relational_fields');
    var rpc = require('web.rpc');
    var _t = core._t;


    var FieldMultiFiles = AbstractField.extend({
        template: "FieldBinaryFileUploader",
        supportedFieldTypes: ['many2many', 'one2many'],
        init: function () {
            this._super.apply(this, arguments);

            if (!_.contains(this.supportedFieldTypes, this.field.type)) {
                var msg = _t("The type of the field '%s' must be a one2many or many2many field.");
                throw _.str.sprintf(msg, this.field.string);
            }

            this.uploadedFiles = {};
            this.uploadingFiles = [];
        },

        destroy: function () {
            this._super();
            $(window).off(this.fileupload_id);
        },

        _onFileLoaded: function (ev, files, rec) {
            var self = this;
            this.uploadingFiles = [];

            var attachment_ids = this.value.res_ids;
            _.each(files, function (file) {
                if (file.error) {
                    self.do_warn(_t('Uploading Error'), file.error);
                } else {
                    attachment_ids.push(file.id);
                    self.uploadedFiles[file.id] = true;
                }
            });

            this.viewType = rec.record.viewType;
            this._setValue({
                operation: 'REPLACE_WITH',
                ids: attachment_ids,
            });
        },
    });


    relational_fields.FieldOne2Many.include({
        _renderButtons: function () {
            var self = this;
            this._super();
            var multy_attach = this.$buttons && this.$buttons.find('.o_button_select_files');
            var attachment_field = this.view.arch.tag === 'kanban' && this.view.arch.attrs.drop_attachments_field;
            if (!this.isReadonly && attachment_field && multy_attach && multy_attach.length) {
                this.drop_att = {};
                this.drop_att.name = this.field.name;
                this.drop_att.model = this.field.relation;
                this.drop_att.field = this.field.relation_field;
                this.drop_att.res_id = this.record.res_id;
                var mf_widget = new FieldMultiFiles(this.getParent(),
                    this.drop_att.name,
                    this.record,
                    {mode: 'edit',}
                );

                // show image attachment button
                multy_attach.parent().attr("style", "display: inline-block;");
                multy_attach.on('change', function(event) {
                    var files = event.currentTarget.files;
                    var imported = self.import_files(event).then(function(res){
                        mf_widget._onFileLoaded(event, self.updated_files, self);
                    });
                });

            }
        },

        import_files: function(event) {
            var self = this;
            this.updated_files = [];

            var deferred_cycle = function(files){
                var file = files.shift();
                var done = $.Deferred();
                var check = typeof file === 'object';
                if (!check) {
                    return done.resolve();
                }

                var reader = new FileReader();
                var def = $.Deferred();
                // Read in the image file as a data URL.
                reader.onloadend = (function(theFile) {
                    var data = theFile.target.result;
                    file.image = data.split(',')[1];
                    file.res_id = self.drop_att.res_id;
                    def.resolve();
                });
                reader.readAsDataURL(file);

                def.then(function(){
                    var arg = {
                        'name': file.name,
                        'image': file.image,
                    };
                    arg[self.drop_att.name] = self.drop_att.res_id;
                    rpc.query({
                        model: self.drop_att.model,
                        method: 'create',
                        args: [arg],
                    }).then(function(res){
                        self.updated_files.push(_.extend(file, {id: res}));
                        if (files.length) {
                            deferred_cycle(files).then(function(){
                                done.resolve();
                            });
                        } else {
                            done.resolve();
                        }
                    });
                });

                return done;
            };

            var files = event.currentTarget.files;
            return deferred_cycle(_.values(_.clone(files)));
        },
    });

});
