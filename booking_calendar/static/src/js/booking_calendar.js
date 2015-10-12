openerp.booking_calendar = function (session) {
    var _t = session.web._t;
    var QWeb = session.web.qweb;
    var bookings = [];

    var is_calendar_closed = false;

    function record_to_event(record) {
    }
    
    session.web.form.One2ManyListView.include({

        create_booking_calendar_iframe: function(record) {
            var venue = record.attributes.venue_id;
            var pitch = record.attributes.pitch_id;
            return $(QWeb.render('BookingCalendarIFrame', {
                        'url': this.session.url('/booking/calendar', {
                            'venue': venue && venue[0] || '',
                            'pitch': pitch && pitch[0] || '',
                            'backend': 1
                        })
                    }))[0];
        },

        do_button_action: function (name, id, callback) {
            var self = this;
            var record = self.records.get(id);
            var venue = record.attributes.venue_id;
            if (name == 'open_calendar') {
                var $iframe = self.create_booking_calendar_iframe(record);
                is_calendar_closed = false;
                var c_dialog = new session.web.Dialog(this, {
                    // dialogClass: 'oe_act_window',
                    size: 'large',
                    title: _t('Booking Calendar'),
                    destroy_on_close: false,
                }, $iframe).open();

                var work_calendar = record.attributes.calendar_id;
                $iframe.onload = function(){
                    this.contentWindow.booking_calendar.initBackend(true, bookings, work_calendar);
                }       

                c_dialog.on('closing', this, function (e){
                    if (is_calendar_closed) {
                        return; // to avoid call on dialog destroying (not closing)
                    }
                    self.start_edition(record, {});
                    _.each($iframe.contentWindow.booking_calendar.bookings, function(b){
                        self.editor.form.fields.resource_id.set({'value': b.resourceId});
                        self.editor.form.fields.booking_start.set({'value': b.start.format("YYYY-MM-DD HH:mm:ss")});
                        self.editor.form.fields.booking_end.set({'value': b.start.add(1, 'hours').format("YYYY-MM-DD HH:mm:ss")});
                    });
                    self.ensure_saved().then(function (done) {
                        is_calendar_closed = true;
                        callback(id);
                    });
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
                    return self.reload_record(self.records.get(id));
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