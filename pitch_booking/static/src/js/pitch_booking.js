openerp.pitch_booking = function (session) {
    var QWeb = session.web.qweb;

    session.web.BookingCalendar.include({
        set_record: function(id) {
            var self = this;
            var record = this.view.records.get(id);
            var venue = record.attributes.venue_id;
            var pitch = record.attributes.pitch_id;
            var model = new session.web.Model("sale.order.line");
            model.call('get_resources', [venue && venue[0] || '', pitch && pitch[0] || ''])
                .then(function(resources){
                    console.log(resources);
                    self.$('#external-events').html(QWeb.render("BookingCalendar.resources", { resources : resources }));
                    self.init_ext_events();
                    self.$calendar.fullCalendar24('refetchEvents');
                });
            this.record_id = id;
        },
    });
}