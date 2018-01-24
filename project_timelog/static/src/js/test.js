odoo.define('project_timelog.Tour', function (require) {
    "use strict";

    var Tour = require('web.Tour');

    Tour.register({
        id: 'project_timelog',
        name: 'Run tracking timer in the Back-End',
        path: '/web#model=project.task&action=project.action_view_task',
        mode: 'test',
        steps: [
            {
                title: 'Click tasks',
                element: '.oe_menu_text:contains("Task"):first',
            },
            {
                title: 'Click on the task card',
                element: '.oe_kanban_card:first',
            },
            {
                title: 'Go to the Timesheet tab',
                element: '.nav.nav-tabs a:contains("Timesheets")',
            },
            {
                title: 'Click the button of edit',
                element: '.oe_form_button_edit',
            },
            {
                title: 'Add new item',
                element: '.oe_form_field_x2many_list_row_add a',
            },
            {
                title: 'Add item description',
                element: '.oe_list_editable .oe_form_required input',
                sampleText: 'test'
            },
            {
                title: 'Save change',
                element: '.oe_form_button_save',
                wait: 1000,
            },
            {
                title: 'Play timer',
                element: '.oe-button[data-field="play_timer"] button',
            },
            {
                title: 'Wait 5s.',
                wait: 5000,
            },
            {
                title: 'Stop timer',
                element: '.oe-button[data-field="stop_timer"] button',
            },
        ],
    });
});
