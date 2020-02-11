odoo.define("project_timelog.tour", function(require) {
    "use strict";

    var core = require("web.core");
    var tour = require("web_tour.tour");

    tour.register(
        "project_timelog_tour",
        {
            url: "/web",
            test: true,
        },
        [
            {
                trigger: 'a.full[href="#"]',
                content: "Click to open app list",
                position: "bottom",
            },
            {
                trigger: 'a.dropdown-item.o_app:contains("Project")',
                content: "Click to enter Project",
                position: "bottom",
            },
            {
                trigger: ".o_kanban_record:first",
                content: "Click on the Project card",
                position: "bottom",
            },
            {
                extra_trigger: '.breadcrumb:contains("Tasks")',
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
                trigger: ".tab-pane.active .o_field_x2many_list_row_add a",
                content: "Add new item",
                position: "bottom",
            },
            {
                trigger: ".o_editable_list .o_input.o_field_widget.o_required_modifier",
                content: "Add item description",
                position: "bottom",
                // Random is to evade unique constraint on subtask
                run:
                    "text Test Subtask " +
                    Math.random()
                        .toString(36)
                        .slice(2),
            },
            {
                trigger: ".o_form_button_save",
                content: "Save change",
                position: "bottom",
            },
            {
                trigger: "button.log-start-timer:last",
                extra_trigger: '.o_form_button_edit:contains("Edit")',
                content: "Play timer",
                position: "bottom",
            },
            {
                trigger: "button.log-stop-timer:last",
                content: "Stop timer",
                position: "bottom",
            },
        ]
    );
});
