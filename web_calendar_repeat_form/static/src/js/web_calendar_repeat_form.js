openerp.web_calendar_repeat_form = function (session) {

    session.web_calendar.CalendarView.include({
        view_loading: function(fv) {
            this.prev_data = {};
            this.repeat_form = false;
            var res =  this._super(fv);
            if (this.quick_create_instance == 'instance.web_calendar_repeat_form.QuickCreateRepeated') {
                this.repeat_form = true;
            }
            return res;
        },
        slow_created: function (data) {
            this._super();
            if (this.repeat_form) {
                this.prev_data = data;
            }
        },
        open_quick_create: function(data_template) {
            if (this.repeat_form) {
                data_template = $.extend({}, this.prev_data, data_template);
            }
            this._super(data_template);
        }
    });

    session.web_calendar_repeat_form.QuickCreateRepeated = session.web_calendar.QuickCreate.extend({
        slow_create: function(data) {
            this.prev_data = {};
            var self = this;
            var def = $.Deferred();
            var defaults = {};
            var created = false;

            _.each($.extend({}, this.data_template, data), function(val, field_name) {
                defaults['default_' + field_name] = val;
            });
                        
            var pop_infos = self.get_form_popup_infos();
            this.pop = new session.web.form.FormOpenPopup(this);
            var context = new session.web.CompoundContext(this.dataset.context, defaults);
            this.pop.show_element(this.dataset.model, null, this.dataset.get_context(defaults), {
                title: this.get_title(),
                disable_multiple_selection: true,
                view_id: pop_infos.view_id,
                create_function: function(data, options) {
                    self.prev_data = data;
                    return self.dataset.create(data, options).done(function(r) {
                    }).fail(function (r, event) {
                       if (!r.data.message) { //else manage by openerp
                            throw new Error(r);
                       }
                    });
                },
                read_function: function(id, fields, options) {
                    return self.dataset.read_ids.apply(self.dataset, arguments).done(function() {
                    }).fail(function (r, event) {
                        if (!r.data.message) { //else manage by openerp
                            throw new Error(r);
                        }
                    });
                },
            });
            this.pop.on('closed', self, function() {
                if (def.state() === "pending") {
                    def.resolve();
                }
            });
            this.pop.on('create_completed', self, function(id) {
                created = true;
                self.trigger('slowadded', self.prev_data);
            });
            def.then(function() {
                if (created) {
                    var parent = self.getParent();
                    parent.$calendar.fullCalendar('refetchEvents');
                }
                self.trigger('close');
            });
            return def;
        }
    });

};
