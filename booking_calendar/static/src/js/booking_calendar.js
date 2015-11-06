openerp.booking_calendar = function (session) {
    var _t = session.web._t;
    var QWeb = session.web.qweb;
    var DTF = 'YYYY-MM-DD HH:mm:ss';
    var MIN_TIME_SLOT = 1; //hours

    session.web.BookingCalendar = session.web.Dialog.extend({
        template: "BookingCalendar",
        bookings: [],
        init: function (parent, options, content) {
            this._super(parent, options);
            this.view = options.view;
            this.bookings = [];
            this.resources = [];
        },
        start: function() {
            this.$calendar = this.$('#calendar');
            this.init_calendar();
        },
        set_record: function(id) {
            var self = this;
            this.record_id = id;
            var model = new session.web.Model("resource.resource");
            model.query(['id', 'name'])
                .filter([['to_calendar', '=', true]])
                .all().then(function (resources) {
                    self.$('#external-events').html(QWeb.render("BookingCalendar.resources", { resources : resources }));
                    self.init_ext_events();
                    self.$calendar.fullCalendar24('refetchEvents');
                });
        },
        init_calendar: function() {
            var self = this;
            this.$calendar.fullCalendar24({
                header: {
                  left: 'prev,next today',
                  center: 'title',
                  right: 'month,agendaWeek,agendaDay'
                },
                dropAccept: '.fc-event',
                handleWindowResize: true,
                height: 'auto',
                editable: true,
                droppable: true, // this allows things to be dropped onto the calendar
                eventResourceField: 'resourceId',
                slotDuration: '01:00:00',
                allDayDefault: false,
                allDaySlot: false,
                defaultTimedEventDuration: '01:00:00',
                displayEventTime: false,
                firstDay: 1,
                defaultView: 'agendaWeek',
                timezone: 'local',
                slotEventOverlap: false,
                events: self.load_events,
                eventReceive: self.event_receive,
                eventOverlap: self.event_overlap,
                eventDrop: self.event_drop,
                eventResize: self.event_drop,
                dialog: self
            });
        },
        init_ext_events: function() {
            var self = this;
            this.resources = [];
            this.$('#external-events .fc-event').each(function() {
                self.resources.push($(this).data('resource'));
                $(this).data('event', {
                    title: $.trim($(this).text()), // use the element's text as the event title
                    stick: true, // maintain when user navigates (see docs on the renderEvent method)
                    resourceId: $(this).data('resource'),
                    borderColor: 'red',
                    color: $(this).data('color'),
                });
                // make the event draggable using jQuery UI
                $(this).draggable({
                    zIndex: 999,
                    revert: true,      // will cause the event to go back to its
                    revertDuration: 0  //  original position after the drag
                })
                .css('background-color', $(this).data('color'))
                .css('border-color', $(this).data('color'));
            });
        },
        load_events: function(start, end, timezone, callback) {
            var self = this;
            var model = new session.web.Model("sale.order.line");
            model.call('get_bookings', [start.format(DTF), end.format(DTF), self.options.dialog.resources])
                .then(function (events) {
                    for(var i = events.length - 1; i >= 0; i--) {
                        var dialog = self.options.dialog;
                        if(dialog.$calendar.fullCalendar24('clientEvents', events[i].id).length) {
                            events.splice(i, 1);
                        }
                    }
                    callback(events);
                });
        },
        update_record: function(event) {
            var start = event.start.clone();
            var end = event.end ? event.end.clone() : start.clone().add(MIN_TIME_SLOT, 'hours');
            var record = this.view.records.get(this.record_id);
            this.view.start_edition(record, {});
            this.view.editor.form.fields.resource_id.set_value(event.resourceId);
            this.view.editor.form.fields.booking_start.set_value(start.utc().format(DTF));
            this.view.editor.form.fields.booking_end.set_value(end.utc().format(DTF));
        },
        event_receive: function(event, allDay, jsEvent, ui) {
            var dialog = this.opt('dialog');
            dialog.$calendar.fullCalendar24('removeEvents', [dialog.record_id]);
            dialog.update_record(event);
            event._id = dialog.record_id;
            dialog.$calendar.fullCalendar24('updateEvent', event);
        },
        event_drop: function(event, delta, revertFunc, jsEvent, ui, view){
            var dialog = view.options.dialog;
            dialog.update_record(event);
        },
        event_overlap: function(stillEvent, movingEvent) {
            return stillEvent.resourceId != movingEvent.resourceId;
        },
        open: function(id) {
            if (this.dialog_inited) {
                var dialog_inited = true;
            }
            var res = this._super();
            this.set_record(id);
            if (dialog_inited) {
                this.$dialog_box.modal('show');
            }
            return res;
        }
    });


    session.web.form.One2ManyListView.include({
        do_button_action: function (name, id, callback) {
            var self = this;
            if (name == 'open_calendar') {
                if (!self.o2m.bc || self.o2m.bc.isDestroyed()) {
                    self.o2m.bc = new session.web.BookingCalendar(this, {
                        // dialogClass: 'oe_act_window',
                        size: 'large',
                        title: _t('Booking Calendar'),
                        destroy_on_close: false,
                        record_id: id,
                        view: self
                    });
                }
                self.o2m.bc.open(id).on('closing', this, function (e){
                    callback(id);
                });
            } else {
                this._super(name, id, callback);    
            }
        },
    });

    session.web.ListView.List.include({
        init: function (group, opts) {
            var self = this;
            this._super(group, opts);
            this.$current.delegate('.oe_button_calendar', 'click', function (e) {
                e.stopPropagation();
                var $target = $(e.currentTarget),
                    $row = $target.closest('tr'),
                    record_id = self.row_id($row);
                if ($target.attr('disabled')) {
                    return;
                }
                $target.attr('disabled', 'disabled');
                
                $(self).trigger('action', ['open_calendar', record_id, function (id) {
                    $target.removeAttr('disabled');
                    // return self.reload_record(self.records.get(id));
                }]);
            });

    }});

    session.web.list.CalButton = session.web.list.Column.extend({
        format: function (row_data, options) {
            options = options || {};
            var attrs = {};
            if (options.process_modifiers !== false) {
                attrs = this.modifiers_for(row_data);
            }
            if (attrs.invisible) { return ''; }
            var template = 'ListView.row.calendar.button';
            return QWeb.render(template, {
                widget: this,
                prefix: session.session.prefix,
                disabled: attrs.readonly
            });
        }
    });

    session.web.list.columns.add('calbutton', 'session.web.list.CalButton');
}