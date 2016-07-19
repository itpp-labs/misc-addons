$(document).ready(function() {
    booking_calendar.domain.push(['venue_id', '=', $('#venues-tab a.active').data('venue')]);
});