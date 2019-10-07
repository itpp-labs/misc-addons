odoo.define('project_timelog.tour', function(require) {
    "use strict";

    var core = require('web.core');
    var tour = require('web_tour.tour');

    tour.register('project_timelog_tour', {
        url: "/web",
        test: true,
    }, [{
        trigger: '.o_app[data-menu-xmlid="project.menu_main_pm"], .oe_menu_toggler[data-menu-xmlid="project.menu_main_pm"]',
        content: "Click the Project menu",
        position: "bottom"
    },{
        trigger: '.oe_menu_text:contains("Task"):first',
        content: "Click the Task menu",
        position: "bottom"
    }, {
        trigger: '.o_kanban_record:first',
        content: "Click on the Task card",
        position: "bottom",
        run: function() {
            // give time to fully load
            setTimeout(function() {
                $('.o_kanban_record:first').trigger("click");
            }, 2000);
        }
    }, {
        trigger: '.nav.nav-tabs a:contains("Timesheets")',
        content: 'Go to the Timesheet tab',
        position: "bottom"
    }, {
        trigger: ".o_form_button_edit",
        content: "Click the button of edit",
        position: "bottom"
    }, {
        trigger: '.tab-pane.active .o_field_x2many_list_row_add a',
        content: 'Add new item',
        position: "bottom"
    }, {
        trigger: ".o_editable_list .o_input.o_field_widget.o_required_modifier",
        content: "Add item description",
        position: "bottom",
        // random is to evade unique constraint on subtask
        run: "text Test Subtask " + Math.random().toString(36).slice(2),
    }, {
        trigger: ".o_form_button_save",
        content: "Save change",
        position: "bottom"
    }, {
        trigger: 'button.log-start-timer:last',
        extra_trigger: '.o_form_button_edit:contains("Edit")',
        content: "Play timer",
        position: "bottom",
    }, {
        trigger: 'button.log-stop-timer:last',
        content: "Stop timer",
        position: "bottom"
    }
    ]);
});
