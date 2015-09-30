openerp.booking_calendar = function (session) {
    var _t = session.web._t,
       _lt = session.web._lt;
    var QWeb = session.web.qweb;
    var bookings = new Array();
    
    session.web.form.BookingCalendarButton = session.web.form.AbstractField.extend({
        template: 'BookingCalendarButton',
        bookings: [],
        init: function(field_manager, node) {
            this._super.apply(this, arguments);
            if (!this.$iframe) {
                this.$iframe = $(QWeb.render('BookingCalendarIFrame', {'url': '/booking/calendar'}))[0];
                this.view.$el.append(this.$iframe);
            }
        },
        start: function() {
            this._super.apply(this, arguments);
            this.set_button();
        },
        set_button: function() {
            var self = this;
            if (this.$button) {
                this.$button.remove();
            }
            this.string = '';
            this.node.attrs.icon = '/booking_calendar/static/src/img/icons/calendar.png';
            this.$button = $(QWeb.render('WidgetButton', {'widget': this}));
            this.$button.addClass('oe_link').css({'padding':'4px'});
            this.$el.html(this.$button);
            this.$button.on('click', self.on_click);
        },
        on_click: function(ev) {

            var dialog = new session.web.Dialog(this, {
                // dialogClass: 'oe_act_window',
                size: 'large',
                title: _t('Booking Calendar'),
                destroy_on_close: false,
            }, this.$iframe).open();

            this.$iframe.onload = function(){
                this.contentWindow.init_backend(true, bookings);         
            }       

            dialog.on('closing', this, function (e){
                var val = [];
                _.each(this.$iframe.contentWindow.bookings, function(b){
                    bookings.push(b);
                    val.push([0, false, {
                        'resource_id': b.resourceId,
                        'date_start': b.start.format("YYYY-MM-DD HH:mm:ss"),
                        'date_end': b.start.add(1, 'hours').format("YYYY-MM-DD HH:mm:ss"),
                    }]);
                });
                this.set('value', val);
            });
            
        },
        set_value: function(value_) {
            var self = this;
            this.set_button();
        }
            
    });
    


    session.web.form.One2ManyListView.include({
        do_button_action: function (name, id, callback) {
            var self = this;
            if (name == 'open_calendar') {
               var $iframe = $(QWeb.render('BookingCalendarIFrame', {'url': session.session.prefix + '/booking/calendar'}))[0];
                var c_dialog = new session.web.Dialog(this, {
                    // dialogClass: 'oe_act_window',
                    size: 'large',
                    title: _t('Booking Calendar'),
                    destroy_on_close: false,
                }, $iframe).open();

                $iframe.onload = function(){
                    this.contentWindow.init_backend(true, bookings);         
                }       

                c_dialog.on('closing', this, function (e){
                    var val = [];
                    _.each($iframe.contentWindow.bookings, function(b){
                        var record = self.records.get(id);
                        if (record) {
                            record.set('booking_start', b.start.format("YYYY-MM-DD HH:mm:ss"));
                            record.set('booking_end', b.start.add(1, 'hours').format("YYYY-MM-DD HH:mm:ss"));
                        }
                    });
                    self.o2m.trigger_on_change();
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


    session.web.form.widgets.add('booking_calendar_button', 'session.web.form.BookingCalendarButton');
    session.web.list.columns.add('calbutton', 'session.web.list.CalButton');

}