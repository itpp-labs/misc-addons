// Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
odoo.define('web_website.tour', function(require) {
"use strict";

var tour = require("web_tour.tour");
var base = require("web_editor.base");

var options = {
    test: true,
    url: '/web#',
    wait_for: base.ready()
};

var tour_name = 'web_website.tour';
tour.register(tour_name, options,
    [
        {
            content: "Toggle Website Switcher",
            trigger: '.o_switch_website_menu > a',
        },
        {
            content: "Click 'All Website'",
            trigger: '.o_switch_website_menu .all_websites'
        },
    ]
);

});
