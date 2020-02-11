odoo.define("res_partner_skype.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");
    var core = require("web.core");
    var _t = core._t;

    var steps = [
        {
            trigger:
                '.o_field_email.o_field_widget.o_form_uri.o_text_overflow[href="skype:skype_test?call"]',
            content: _t("Check the link"),
            position: "bottom",
            timeout: 60000,
        },
    ];

    tour.register(
        "tour_res_partner_skype",
        {test: true, url: "/web#id=9&view_type=form&model=res.partner"},
        steps
    );
});
