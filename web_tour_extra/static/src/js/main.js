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
			window.location.hash = window.location.hash.replace(/[&][/]#tutorial.*=true/, "");
			window.location.hash = window.location.hash.replace(/tutorial.*=true/, "");
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
	$(document).ready(function () {
    if (Tour.autoRunning) {
        Tour.running();
    };
});

};
