(function () {
    'use strict';

    var website = openerp.website;
    var _t = openerp._t;

    website.add_template_file('/website_files/static/src/xml/website_files.editor.xml?'+Math.random());

    website.editor.LinkDialog.include({
        start: function(){
            var self = this;
            var last;
            this.$('#link-file').select2({
                minimumInputLength: 1,
                placeholder: _t("File name"),
                query: function (q) {
                    if (q.term == last) return;
                    last = q.term;
                    $.when(
                        self.fetch_files(q.term)
                    ).then(function (results) {
                        var rs = _.map(results, function (r) {
                            return { id: r.website_file_url, text: r.datas_fname};
                        });
                        q.callback({
                            more: false,
                            results: rs
                        });
                    }, function () {
                        q.callback({more: false, results: []});
                    });
                },
            });
            return this._super();
        },
        fetch_files: function (term) {
            return this.call('search_files', [null, term], {
                limit: 9,
                context: website.get_context(),
            });
        },

    })

    website.editor.MediaDialog.include({
        start: function () {
            var self = this;
            this.fileDialog = new website.editor.FileDialog(this, this.editor, this.media);
            this.fileDialog.appendTo(this.$("#editor-media-file"));

            $('a[data-toggle="tab"]').on('shown.bs.tab', function (event) {
                if ($(event.target).is('[href="#editor-media-file"]')) {
                    self.active = self.fileDialog;
                    self.$('li.search-file, li.previous-file, li.next-file').removeClass("hidden");
                    self.$('li.search:has(form)').removeClass("hidden");
                    self.$('li.previous, li.next').addClass("hidden");
                } else {
                    self.$('li.search-file, li.previous-file, li.next-file').addClass("hidden");
                }
            });
            if (this.media) {
                if (this.media.$.nodeName === "A") {
                    this.$('[href="#editor-media-file"]').tab('show');
                }
            }
            return this._super();
        },
        save: function(){
            var self = this;
            if (self.media) {
                if (this.active !== this.fileDialog) {
                    this.fileDialog.clear();
                }
            }
            return this._super();
        }
    })

    var FILES_PER_PAGE = 30;
    website.editor.FileDialog = website.editor.Media.extend({
        template: 'website.editor.dialog.file',
        events: _.extend({}, website.editor.Dialog.prototype.events, {
            'click button.filepicker': function () {
                var filepicker = this.$('input[type=file]');
                if (!_.isEmpty(filepicker)){
                    filepicker[0].click();
                }
            },
            'change input[type=file]': 'file_selection',
            'submit form': 'form_submit',
            'click .existing-attachments-files tr.file': 'select_existing',
            'click .existing-attachment-file-remove': 'try_remove',
        }),

        init: function (parent, editor, media) {
            this.page = 0;
            this._super(parent, editor, media);
        },
        start: function () {
            var self = this;
            var res = this._super();

            var o = { url: null, file_name: null };
            // avoid typos, prevent addition of new properties to the object
            Object.preventExtensions(o);
            this.trigger('start', o);

            this.parent.$(".search-file>.pager > li").click(function (e) {
                e.preventDefault();
                var $target = $(e.currentTarget);
                if ($target.hasClass('disabled')) {
                    return;
                }
                self.page += $target.hasClass('previous-file') ? -1 : 1;
                self.display_attachments();
            });

            this.set_file(o.url, o.file_name);

            return res;
        },
        save: function () {
            if (!this.link) {
                this.link = this.$(".existing-attachments-files img:first").attr('src');
            }
            this.trigger('save', {
                url: this.link
            });
            this.media.renameNode("a");
            this.media.$.innerHTML = this.file_name
            $(this.media).attr('href', this.link);
            return this._super();
        },
        clear: function () {
            this.media.$.className = this.media.$.className.replace(/(^|\s)(img(\s|$)|img-[^\s]*)/g, ' ');
        },
        cancel: function () {
            this.trigger('cancel');
        },

        change_input: function (e) {
            var $input = $(e.target);
            var $button = $input.parent().find("button");
            if ($input.val() === "") {
                $button.addClass("btn-default").removeClass("btn-primary");
            } else {
                $button.removeClass("btn-default").addClass("btn-primary");
            }
        },

        search: function (needle) {
            var self = this;
            this.fetch_existing(needle).then(function () {
                self.selected_existing(self.$('input.url').val());
            });
        },

        set_file: function (file_name, url, error) {
            var self = this;
            if (url) this.link = url;
            if (file_name) this.file_name = file_name;
            this.$('input.url').val('');
            this.fetch_existing().then(function () {
                self.selected_existing(url);
            });
        },

        form_submit: function (event) {
            var self = this;
            var $form = this.$('form[action="/website/attach_file"]');
            if (!$form.find('input[name="upload"]').val().length) {
                return false;
                // url is not used
                /*
                var url = $form.find('input[name="url"]').val();
                if (this.selected_existing(url).size()) {
                    event.preventDefault();
                    return false;
                }
                 */
            }
            var callback = _.uniqueId('func_');
            this.$('input[name=func]').val(callback);
            window[callback] = function (file_name, url, error) {
                delete window[callback];
                self.file_selected(file_name, url, error);
            };
        },
        file_selection: function () {
            this.$el.addClass('nosave');
            this.$('form').removeClass('has-error').find('.help-block').empty();
            this.$('button.filepicker').removeClass('btn-danger btn-success');
            this.$('form').submit();
        },
        file_selected: function(file_name, url, error) {
            var $button = this.$('button.filepicker');
            if (!error) {
                $button.addClass('btn-success');
            } else {
                url = null;
                this.$('form').addClass('has-error')
                    .find('.help-block').text(error);
                $button.addClass('btn-danger');
            }
            this.set_file(file_name, url, error);
            // auto save and close popup
            this.parent.save();
        },

        fetch_existing: function (needle) {
            var domain = [['website_file', '=', true]];
            if (needle && needle.length) {
                domain.push('|', ['datas_fname', 'ilike', needle], ['name', 'ilike', needle]);
            }
            return openerp.jsonRpc('/web/dataset/call_kw', 'call', {
                model: 'ir.attachment',
                method: 'search_read',
                args: [],
                kwargs: {
                    fields: ['name', 'write_date', 'datas_fname', 'website_file_url', 'website_file_count', 'file_size'],
                    domain: domain,
                    order: 'write_date desc',
                    context: website.get_context(),
                }
            }).then(this.proxy('fetched_existing'));
        },
        fetched_existing: function (records) {
            this.records = records;
            this.display_attachments();
        },
        display_attachments: function () {
            this.$('.help-block').empty();
            var per_screen = FILES_PER_PAGE;

            var from = this.page * per_screen;
            var records = this.records;

            var cur_records = _(records).chain()
                .slice(from, from + per_screen)
                .value();

            this.$('.existing-attachments-files').replaceWith(
                openerp.qweb.render(
                    'website.editor.dialog.file.existing.content', {cur_records: cur_records}));
            this.parent.$('.pager')
                .find('li.previous-file').toggleClass('disabled', (from === 0)).end()
                .find('li.next-file').toggleClass('disabled', (from + per_screen >= records.length));
        },
        select_existing: function (e) {
            var download = $(e.currentTarget).find('.download');
            var link = download.attr('href')
            var file_name = download.attr('title')
            this.link = link;
            this.file_name = file_name;
            this.selected_existing(link);
        },
        selected_existing: function (link) {
            this.$('.existing-attachments-files .file.media_selected').removeClass("media_selected");
            var $select = this.$('.existing-attachments-files .file').filter(function () {
                return $(this).find('.download').attr("href") == link;
            }).first();
            $select.addClass("media_selected");
            return $select;
        },

        try_remove: function (e) {
            var $help_block = this.$('.help-block').empty();
            var self = this;
            var $a = $(e.target);
            var id = parseInt($a.data('id'), 10);
            var attachment = _.findWhere(this.records, {id: id});
            var $both = $a.parent().children();

            $both.css({borderWidth: "5px", borderColor: "#f00"});

            return openerp.jsonRpc('/web/dataset/call_kw', 'call', {
                model: 'ir.attachment',
                method: 'try_remove_file',
                args: [],
                kwargs: {
                    ids: [id],
                    context: website.get_context()
                }
            }).then(function (prevented) {
                if (_.isEmpty(prevented)) {
                    self.records = _.without(self.records, attachment);
                    self.display_attachments();
                    return;
                }
                $both.css({borderWidth: "", borderColor: ""});
                $help_block.replaceWith(openerp.qweb.render(
                    'website.editor.dialog.image.existing.error', {
                        views: prevented[id]
                    }
                ));
            });
        },
    });


})();