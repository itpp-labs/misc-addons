odoo.define('account_accountant.tour', function(require) {
"use strict";

var core = require('web.core');
var tour = require('web_tour.tour');

var _t = core._t;

tour.register('account_reports_widgets', {
    test: true,
    url: '/web?#action=account_reports.action_account_report_pnl',
    },
     [
        {
            content:    "wait web client",
            trigger:    ".o_account_reports_body",
            extra_trigger: ".breadcrumb",
            run: function() {}
        },
        {
            content: "unfold line",
            trigger: '.js_account_report_foldable:first',
            run: 'click',
        },
        {
            content: "check that line has been unfolded",
            trigger: '[data-parent-id]',
        },
        {
            content: 'Open dropdown menu of one of the unfolded line',
            trigger: '[data-parent-id] .o_account_report_line a:first',
            run: 'click',
        },
        {
            content: 'click on the annotate action',
            trigger: '[data-parent-id] .o_account_report_line .o_account_reports_domain_dropdown:first .js_account_reports_add_footnote',
            run: 'click',
        },
        {
            content: 'insert footnote text',
            trigger: '.js_account_reports_footnote_note',
            run: 'text My awesome footnote!'
        },
        {
            content: 'save footnote',
            trigger: '.modal-footer .btn-primary',
            run: 'click'
        },
        {
            content: 'wait for footnote to be saved',
            trigger: '.footnote#footnote1 .text:contains(1. My awesome footnote!)',
            extra_trigger: '.o_account_reports_footnote_sup a[href="#footnote1"]',
        },
        {
            content:      "change date filter",
            trigger:    ".o_account_reports_filter_date > a",
        },
        {
            content:      "change date filter",
            trigger:    ".dropdown-item.js_account_report_date_filter[data-filter='last_year']",
            run: 'click'
        },
        {
            content:      "wait refresh",
            trigger:    ".o_account_reports_level2:last() .o_account_report_column_value:contains(0.00)"
        },
        {
            content:      "change comparison filter",
            trigger:    ".o_account_reports_filter_date_cmp > a"
        },
        {
            content:      "change comparison filter",
            trigger:    ".dropdown-item.js_foldable_trigger[data-filter='previous_period_filter']"
        },
        {
            content:      "change comparison filter",
            trigger:    ".js_account_report_date_cmp_filter[data-filter='previous_period']",
            run: 'click',
        },
        {
            content:      "wait refresh, report should have 4 columns",
            trigger:    "th + th + th + th"
        },
        {
            content:      "click summary",
            trigger: '.o_account_reports_summary',
            run: 'click'
        },
        {
            content:      "edit summary",
            trigger:    'textarea[name="summary"]',
            run: 'text v9 accounting reports are fabulous !'
        },
        {
            content:      "save summary",
            trigger:    '.js_account_report_save_summary',
            run: 'click'
        },
        {
            content:      "wait refresh and check that summary has been saved",
            trigger:    ".o_account_reports_summary:visible:contains(v9 accounting reports are fabulous !)",
            run: function(){}
        },
        {
            content:      "change boolean filter",
            trigger:    ".o_account_reports_filter_bool > a",
        },
        {
            content:      "change cash basis filter",
            trigger:    ".dropdown-item.js_account_report_bool_filter[data-filter='cash_basis']",
            run: 'click'
        },
        {
            title:      "export xlsx",
            trigger:    'button[action="print_xlsx"]',
            run: 'click'
        },
    ]
);

tour.register('account_accountant_tour', {
    'skip_enabled': true,
}, [{
    trigger: '.o_app[data-menu-xmlid="account_accountant.menu_accounting"]',
    content: _t('Ready to discover your new favorite <b>accounting app</b>? Get started by clicking here.'),
    position: 'bottom',
}, {
    trigger: ".o_invoice_new",
    extra_trigger: 'div.o_view_controller:not(.o_has_banner) .o_account_kanban',
    content:  _t("Let\'s start with a new customer invoice."),
    position: "bottom"
}, {
    trigger: ".breadcrumb-item:not(.active):last",
    extra_trigger: "[data-id='open'].btn-primary, [data-id='open'].oe_active",
    content:  _t("Use the path to quickly click back to <b>previous screens</b>, without reloading the page."),
    position: "bottom"
}, {
    trigger: 'li a[data-menu-xmlid="account.menu_finance_reports"], div[data-menu-xmlid="account.menu_finance_reports"]',
    content: _t("Your reports are available in real time. <i>No need to close a fiscal year to get a Profit &amp; Loss statement or view the Balance Sheet.</i>"),
    position: "bottom"
}]);

});
