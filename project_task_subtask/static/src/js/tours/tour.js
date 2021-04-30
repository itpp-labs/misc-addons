odoo.define("project_task_subtask.tour", function (require) {
    "use strict";

    var core = require("web.core");
    var tour = require("web_tour.tour");

    var _t = core._t;

    var steps = [
        tour.STEPS.SHOW_APPS_MENU_ITEM,
        {
            trigger: '.o_app[data-menu-xmlid="project.menu_main_pm"]',
            content: _t(
                "Want a better way to <b>manage your projects</b>? <i>It starts here.</i>"
            ),
            position: "right",
            edition: "community",
        },
        {
            trigger: '.o_app[data-menu-xmlid="project.menu_main_pm"]',
            content: _t(
                "Want a better way to <b>manage your projects</b>? <i>It starts here.</i>"
            ),
            position: "bottom",
            edition: "enterprise",
        },
        {
            trigger: ".o_project_kanban_main",
            content: "open project",
            timeout: 10000,
        },
        {
            trigger: ".o_loading",
            content: "waiting for loading to finish",
            timeout: 5000,
            run: function () {
                // It's a check
            },
        },
        {
            trigger: ".o_content",
            content: "just click",
            timeout: 1000,
        },
        {
            trigger: ".oe_kanban_content",
            content: "open task",
            timeout: 20000,
        },
        {
            trigger: ".o_pager_sort",
            content: "sort",
            timeout: 10000,
        },
        {
            trigger: ".o_pager_unsort",
            content: "unsort",
            timeout: 10000,
        },
    ];

    tour.register("task_subtask", {url: "/web"}, steps);
});
