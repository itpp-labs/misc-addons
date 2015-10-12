(function (self, $) {
    
    self.bookings = [];

    self.initBackend = function(isBackend, bookings, workCalendar) {
        self.isBackend = isBackend;
        self.$calendar.fullCalendar({
            events: bookings
        });
        self.workCalendar = workCalendar;
    };

    self.storeEvent =  function(event) {
        self.bookings.push(event);
    };

    self.eventReceive = function(event) {
        if(self.isBackend) {
            self.storeEvent(event);
        } else {
            self.addEvent(event);
        }
    };

}(window.booking_calendar = window.booking_calendar || {}, jQuery));