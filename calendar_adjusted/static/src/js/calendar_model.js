odoo.define("calendar_adjusted.CalendarModel", function (require) {
    "use strict";
    var CalendarModel = require("web.CalendarModel");

    return CalendarModel.include({
        /*
          Code bellow could be used in v14
        _getFullCalendarOptions: function(){
            const options = this._super.apply(this, arguments);
            options.timeGridEventMinHeight = 70;
            return options;
        }
        */
    });
});
