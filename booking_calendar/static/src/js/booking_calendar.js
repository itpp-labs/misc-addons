openerp.booking_calendar = function (session) {
    var _t = session.web._t;
    var QWeb = session.web.qweb;
    var SLOT_START_DELAY_MINS = 15; //minutes
    var SLOT_MINUTES = 60; //minutes

    function date_to_utc(dt) {
        return new Date(dt.getUTCFullYear(),dt.getUTCMonth(),dt.getUTCDate(),
            dt.getUTCHours(), dt.getUTCMinutes(), dt.getUTCSeconds());
    }

    session.web_calendar.CalendarView.include({
        init: function (parent, dataset, view_id, options) {
            this._super(parent, dataset, view_id, options);
            this.color_code_map = {};
            this.read_resource_color_def = {}
            this.last_domain = {};
        },
        event_data_transform: function(evt) {
            var res = this._super(evt);
            var self = this;
            if (this.read_color) {
                var color_key = evt[this.color_field];
                if (typeof color_key === "object") {
                    color_key = color_key[0];
                }
                
                this.read_resource_color(color_key).done(function(color){
                    if (color) {
                        res.color = color;
                        var event_objs = self.$calendar.fullCalendar('clientEvents', res.id);
                        if (event_objs.length == 1) { // Already existing obj to update
                            var event_obj = event_objs[0];
                            // update event_obj
                            event_obj.color = color;
                            self.$calendar.fullCalendar('updateEvent', event_obj);
                        }
                    }
                });
            }
            if (this.free_slots) {
                res.editable = false;
            }
            return res;
        },
        get_range_domain: function(domain, start, end) {
            //fix timezones
            return this._super(domain, date_to_utc(start), date_to_utc(end));
        },
        do_search: function(domain, context, _group_by) {
            this.last_domain = domain;
            this._super(domain, context, _group_by);
            this.set_free_slot_source(domain);
        },
        set_free_slot_source: function(domain) {
            var self = this;
            if (! _.isUndefined(this.free_slot_source)) {
                this.$calendar.fullCalendar('removeEventSource', this.free_slot_source);
            }
            this.free_slot_source = {
                events: function(start, end, callback) {
                    if(end.getTime() - start.getTime() > 7*25*3600*1000) {
                        return callback();
                    }
                    var d = new Date();
                    var model = new session.web.Model("sale.order.line");
                    model.call('get_free_slots', [start, end, d.getTimezoneOffset(), domain || []])
                        .then(function (slots) {
                            self.now_filter_ids = [];
                            var color_field = self.fields[self.color_field];
                            _.each(slots, function (e) {
                                var key = e[self.color_field];
                                if (!self.all_filters[key]) {
                                    filter_item = {
                                        value: key,
                                        label: e['title'],
                                        color: self.get_color(key),
                                        is_checked: true
                                    };
                                    self.all_filters[key] = filter_item;
                                }
                                if (! _.contains(self.now_filter_ids, key)) {
                                    self.now_filter_ids.push(key);
                                }
                            });
                            if (self.sidebar) {
                                self.sidebar.filter.events_loaded();
                                self.sidebar.filter.set_filters();
                                slots = $.map(slots, function (e) {
                                    var key = e[self.color_field];
                                    if (_.contains(self.now_filter_ids, key) &&  self.all_filters[key].is_checked) {
                                        return e;
                                    }
                                    return null;
                                });
                            }
                            callback(slots);
                        });
                },
                allDayDefault: false
            }
            this.$calendar.fullCalendar('addEventSource', this.free_slot_source);
        },
        free_slot_click_data: function(event) {
            var self = this;
            var patt = /resource_(\d+)/;
            var data_template = self.get_event_data({
                start: event.start,
                end: event.end,
                allDay: false,
            });
            _.each(event.className, function(n){
                var r = patt.exec(n);
                if (r) {
                    data_template[self.color_field] = parseInt(r[1]);
                }
            });
            return data_template;
        },
        get_fc_init_options: function() {
            var res = this._super();
            var self = this;
            if (self.free_slots) {
                res.lazyFetching = false;
                res.eventRender = function(event, element, view) {
                    if (view.name == 'month' && event.className.indexOf('free_slot') >= 0) {
                        return false;
                    }
                }
                res.eventClick = function (event) {
                    if (event.className.indexOf('free_slot') >= 0) {
                        var d = new Date();
                        d.setTime(d.getTime() - SLOT_START_DELAY_MINS*60000);
                        if (event.start < d) {
                            return;
                        }
                        self.open_quick_create(self.free_slot_click_data(event));
                    } else {
                        self.open_event(event._id,event.title);
                    }
                };
                res.timeFormat = {
                    'agenda': '',
                    '': ''
                };
                res.slotMinutes = SLOT_MINUTES;
                res.snapMinutes = SLOT_MINUTES;
            }
            res.firstHour = 6;
            res.slotEventOverlap = false;
            return res;
        },
        select: function (self, start_date, end_date, all_day, _js_event, _view) {
            var is_day = false;
            if (_view.name == 'month') {
                $(document.elementsFromPoint(_js_event.originalEvent.x, _js_event.originalEvent.y)).each(function(){
                    if ($(this).hasClass('fc-day-number')) {
                        _view.calendar.changeView('agendaDay');
                        _view.calendar.gotoDate(start_date);
                        is_day = true;
                        return;
                    }
                });
            }
            if (is_day) {
                return;
            }
            var d = new Date();
            d.setTime(d.getTime() - SLOT_START_DELAY_MINS*60000);
            if (start_date < d) {
                self.$calendar.fullCalendar('unselect');
                return;
            }
            var data_template = self.get_event_data({
                start: start_date,
                end: end_date,
                allDay: all_day,
            });
            self.open_quick_create(data_template);

        },
        read_resource_color: function(key) {
            if (this.read_resource_color_def[key])
                return this.read_resource_color_def[key]

            var self = this;
            var def = $.Deferred();
            if (key in this.color_code_map) {
                def.resolve(this.color_code_map[key]);
            }
            else {            
                new session.web.Model(this.model).call('read_color', [key]).then(function(result) {
                    self.read_resource_color_def[key] = false
                    self.color_code_map[key] = result;
                    def.resolve(result);
                });
            }
            this.read_resource_color_def[key] = def;
            return def;
        },
        
        view_loading: function (fv) {
            var res =  this._super(fv);
            var attrs = fv.arch.attrs;
            this.read_color = false;
            this.free_slots;
            if (attrs.read_color) {
                this.read_color = attrs.read_color;
            }
            if (attrs.free_slots) {
                this.free_slots = attrs.free_slots;
            }
            return res
        },
        remove_event: function(id) {
            var id = parseInt(id);
            return this._super(id);
        },
        open_quick_create: function(data_template) {
            this._super(data_template);
            if (this.free_slots) {
                var self = this;
                var pop = this.quick.pop;
                pop.view_form.on("form_view_loaded", pop, function() {
                    var $sbutton = this.$buttonpane.find(".oe_abstractformpopup-form-save");
                    var $sobutton = $(_t("<button>Save & Open SO</button>"));
                    $sbutton.after($sobutton);
                    $sobutton.click(function() {
                        $.when(pop.view_form.save()).done(function(line_id) {
                            pop.view_form.reload_mutex.exec(function() {
                                pop.check_exit();
                                self.dataset.read_slice(['order_id'], {domain:[['id', '=', line_id]]})
                                    .then(function(records){
                                        self.do_action({
                                            'type': 'ir.actions.act_window',
                                            'res_model': 'sale.order',
                                            'res_id': records[0]['order_id'][0],
                                            'target': 'current',
                                            'views': [[false, 'form'], [false, 'list']],
                                            'context': {}
                                        });
                                    });
                            });
                        });
                    });
                });
            }
        },
    });

    session.web_calendar.SidebarFilter.include({
        set_filters: function() {
            this._super();
            if (this.view.read_color) {
                var self = this;
                _.forEach(self.view.all_filters, function(o) {
                    if (_.contains(self.view.now_filter_ids, o.value)) {
                        self.view.read_resource_color(o.value).done(function (color) {
                            self.$('div.oe_calendar_responsible span.underline_color_' + o.color).css('border-color', color);
                        });
                    }
                });
            }
        },
    });
}
