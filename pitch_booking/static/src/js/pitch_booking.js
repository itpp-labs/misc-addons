openerp.pitch_booking = function (session) {

    session.web_calendar.CalendarView.include({
        free_slot_click_data: function(event) {
            var data_template = this._super(event);
            data_template['pitch_id'] = data_template['resource_id'];
            delete data_template['resource_id'];
            return data_template;
        }
    });
}