// Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
// Copyrigth 2019 Eugene Molotov <https://it-projects.info/team/em230418>
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
odoo.define("web_website.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");

    var options = {
        test: true,
        url: "/web#",
    };

    var tour_name = "web_website.tour";
    tour.register(tour_name, options, [
        {
            content: "Toggle Website Switcher",
            trigger: ".o_switch_website_menu > a",
        },
        {
            content: "Click Website localhost",
            trigger: ".o_switch_website_menu a[data-website-id=1]",
        },
        {
            content: "Wait when page is reloaded",
            trigger: ".o_switch_website_menu > a:contains(My Website)",
            // Mail module is installed as a part of depencies.
            // It's assumed, that Discuss menu is the default menu
            extra_trigger: ".o_mail_discuss_sidebar",
        },
    ]);
});
