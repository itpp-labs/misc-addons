odoo.define("calendar_adjusted.CalendarView", function (require) {
    "use strict";
    /* eslint-disable init-declarations */
    var CalendarView = require("web.CalendarView");

    return CalendarView.include({
        getController: function () {
            return this._super.apply(this, arguments).then(function () {
                // Patch fullCalendar
                const eventMinHeight = 25;
                $.fullCalendar.TimeGrid.prototype.computeSegVerticals = function (
                    segs
                ) {
                    var i, seg;

                    for (i = 0; i < segs.length; i++) {
                        seg = segs[i];
                        seg.top = this.computeDateTop(seg.start, seg.start);
                        // Original code in fullCalendar v3:
                        // seg.bottom = this.computeDateTop(seg.end, seg.start);
                        seg.bottom = Math.max(
                            seg.top + eventMinHeight,
                            this.computeDateTop(seg.end, seg.start)
                        );
                    }
                };
                return Promise.resolve(...arguments);
            });
        },
    });
});
