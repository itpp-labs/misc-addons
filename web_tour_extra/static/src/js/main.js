odoo.define('web_tour_extra.Tour', function (require) {
    "use strict";

    var core = require('web.core');

    var _t = core._t;
    var qweb = core.qweb;
    var Tour = require('web.Tour');

    Tour.getState = function () {
        var state = JSON.parse(localStorage.getItem("tour") || 'false') || {};
        if (state) {
            this.time = state.time;
        }
        var tour_id, mode, step_id;
        // tutorial_extra instead of tutorial
        if (!state.id && window.location.href.indexOf("#tutorial_extra.") > -1) {
            this.tutorial_extra = true;
            state = {
                "id": window.location.href.match(/#tutorial_extra\.(.*)=true/)[1],
                "mode": "tutorial",
                "step_id": 0
            };
            // Do not clean hash for reasons of saving starting tour path.
            window.location.hash = window.location.hash.replace(RegExp("&?/?#tutorial[^=]*=true"), "");
            Tour.log("Tour '" + state.id + "' Begin from url hash");
            Tour.saveState(state.id, state.mode, state.step_id, 0, state.log);
        }
        else if (!state.id && window.location.href.indexOf("#tutorial.") > -1) {
            state = {
                "id": window.location.href.match(/#tutorial\.(.*)=true/)[1],
                "mode": "tutorial",
                "step_id": 0
            };
            window.location.hash = "";
            Tour.log("Tour '"+state.id+"' Begin from url hash");
            Tour.saveState(state.id, state.mode, state.step_id, 0, state.log);
        }
        if (!state.id) {
            return;
        }
        state.tour = Tour.tours[state.id];
        state.step = state.tour && state.tour.steps[state.step_id === -1 ? 0 : state.step_id];
        return state;
    };
    // below fix of backend popover bug when element can't get in time and some old stuff is pooped
    var super_closePopover = Tour.closePopover;
    Tour.closePopover = function () {
        if (Tour.$element) {
            Tour.$element.data('bs.popover', false)
        }
        super_closePopover.call(this)
    };
});
