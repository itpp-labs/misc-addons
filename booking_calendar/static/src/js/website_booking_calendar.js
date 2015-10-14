(function (self, $) {
    
    self.initBackend = function(isBackend, bookings, workCalendar) {
        self.isBackend = isBackend;
        self.$calendar.fullCalendar({
            events: bookings
        });
        self.workCalendar = workCalendar;
    };

    self.validate = function(event) {
        $.ajax({
            url: '/booking/calendar/validate',
            dataType: 'json',
            contentType: 'application/json',
            type: 'POST',
            data: JSON.stringify({params: {
                // our hypothetical feed requires UNIX timestamps
                start: event.start.format("YYYY-MM-DD HH:mm:ss"),
                end: event.end.format("YYYY-MM-DD HH:mm:ss"),
                calendar: self.workCalendar
            }}),
            success: function(response) {
                console.log(response);
            }
        });
    }

}(window.booking_calendar = window.booking_calendar || {}, jQuery));