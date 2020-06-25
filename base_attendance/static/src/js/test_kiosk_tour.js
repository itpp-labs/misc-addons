/* Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
   License MIT (https://opensource.org/licenses/MIT). */
odoo.define("base_attendance.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");
    var core = require("web.core");
    var _t = core._t;

    function partner_check_in_out(partner, color) {
        return [
            {
                extra_trigger: ".o_hr_attendance_kiosk_mode_container",
                trigger: '.o_hr_attendance_button_partners:contains("Select Partner")',
                content: "Click Select Partner button",
            },
            {
                trigger:
                    ".oe_kanban_global_click.o_kanban_record:contains(" +
                    partner +
                    ") " +
                    ".oe_hr_attendance_status.fa.fa-user.oe_hr_attendance_status_" +
                    color,
                content: "Select Partner",
            },
            {
                trigger: "body.o_web_client.o_fullscreen",
                content: "Dummy action in order to prevent a freaky issue",
            },
            {
                extra_trigger: "body.o_web_client.o_fullscreen:not(.oe_wait)",
                trigger: ".fa.btn-primary.o_hr_attendance_sign_in_out_icon",
                content: "Check in",
            },
            {
                trigger: 'button:contains("ok")',
                content: "Validate",
            },
        ];
    }

    var steps = [
        {
            trigger: 'a.full[href="#"]',
            content: _t("Click to open app list"),
            position: "bottom",
        },
        {
            trigger: 'a.dropdown-item.o_app:contains("Attendance")',
            content: _t("Click to enter menu attendances"),
            position: "bottom",
        },
        {
            trigger:
                'a.dropdown-toggle.o-no-caret.o_menu_header_lvl_1:contains("Attendance")',
            content: _t("Click to open Manage Attendances menu"),
        },
        {
            trigger: 'a.dropdown-item.o_menu_entry_lvl_2:contains("Kiosk")',
            content: _t("Click to enter Kiosk"),
        },
    ];

    steps = steps.concat(partner_check_in_out("Brandon Freeman", "red"));
    steps = steps.concat(partner_check_in_out("Brandon Freeman", "green"));

    tour.register("test_kiosk_tour", {test: true, url: "/web"}, steps);
});
