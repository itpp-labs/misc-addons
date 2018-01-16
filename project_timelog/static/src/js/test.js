odoo.define('point_of_sale.Tour', function (require) {
    "use strict";

    var Tour = require('web.Tour');

    Tour.register({
        id: 'project_timelog',
        name: 'Run tracking timer in the Back-End',
        path: '/web?debug',
        mode: 'test',
        steps: [
            {
                title: 'Go to the Project menu',
                wait: 200,
                element: '.oe_menu_toggler[data-menu="190"]',
            },
            {
                title: 'Click tasks',
                element: '.oe_menu_leaf[data-menu="193"]',
            },
            {
                title: 'Click on the task card',
                element: '.oe_kanban_card',
            },
            {
                title: 'Go to the Timesheet tab',
                element: 'a[href="#notebook_page_94"]',
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
            },
        ],
    });
});
