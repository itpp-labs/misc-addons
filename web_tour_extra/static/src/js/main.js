openerp.web_tour_extra = function(instance) {
    var Tour = instance.web.Tour;

    instance.web.Tour.getState = function () {
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
            Tour.saveState(state.id, state.mode, state.step_id, 0);
        }
        if (!state.id) {
            return;
        }
        state.tour = Tour.tours[state.id];
        state.step = state.tour && state.tour.steps[state.step_id === -1 ? 0 : state.step_id];
        return state;
    };
    var super_autoTogglePopover = Tour.autoTogglePopover;
    instance.web.Tour.autoTogglePopover = function () {
        var state = Tour.getState();
        var step = state.step;
        var $element = $(step.element).first();
        if (step.title) {
            // delete title from $element in order to prevent replacing title
            // by $element.attr('title') in fixTitle function in web/static/lib/bootstrap/js/boostrap.js
            var title = $element.attr('title');
            $element.attr('title', null);
        }
        super_autoTogglePopover.call(this);
        // return title back
        $element.attr('title', title);
    };
    $(document).ready(function () {
    // if there 'tour' in localStorage, then tour is already running and we don't need to run it again
    // Otherwise we have to call running again, because built-in call doesn't use overwritten function getStorage and doesn't handle tutorial_extra.*=true url
    if(localStorage.getItem("tour"))
    {return};
    if (Tour.autoRunning) {
        Tour.running();
    };
});

};
