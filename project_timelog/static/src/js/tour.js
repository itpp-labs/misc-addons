odoo.define("project_timelog.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "project_timelog_tour",
        {
            url: "/web",
            test: true,
        },
        [
            {
                trigger:
                    '.o_app[data-menu-xmlid="project.menu_main_pm"], .oe_menu_toggler[data-menu-xmlid="project.menu_main_pm"]',
                content: "Click the Project menu",
                position: "bottom",
            },
            {
                trigger: '.oe_menu_text:contains("Task"):first',
                content: "Click the Task menu",
                position: "bottom",
            },
            {
                trigger: ".o_kanban_record:first",
                content: "Click on the Task card",
                position: "bottom",
            },
            {
                trigger: '.nav.nav-tabs a:contains("Timesheets")',
                content: "Go to the Timesheet tab",
                position: "bottom",
            },
            {
                trigger: ".o_form_button_edit",
                content: "Click the button of edit",
                position: "bottom",
            },
            {
                trigger: ".tab-pane.active .o_form_field_x2many_list_row_add a",
                content: "Add new item",
                position: "bottom",
            },
            {
                trigger: ".o_list_editable .o_form_input.o_form_field.o_form_required",
                content: "Add item description",
                position: "bottom",
                run: "text Test Subtask",
            },
            {
                trigger: ".o_form_button_save",
                content: "Save change",
                position: "bottom",
            },
            {
                trigger: 'td[data-field="play_timer"] button',
                content: "Play timer",
                position: "bottom",
            },
            {
                trigger: 'td[data-field="stop_timer"] button',
                content: "Stop timer",
                position: "bottom",
            },
        ]
    );
});
