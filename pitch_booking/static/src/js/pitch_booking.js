openerp.pitch_booking = function (session) {
    var QWeb = session.web.qweb;
    
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
        }
    });
}