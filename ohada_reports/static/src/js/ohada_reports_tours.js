odoo.define('ohada_reports.tour', function (require) {
'use strict';

var Tour = require('web_tour.tour');

Tour.register('account_followup_reports_widgets', {
    test: true,
    url: '/web#action=ohada_reports.action_view_list_customer_statements',
    },
     [
        { 
            content: 'wait for web client',
            trigger: ".o_list_view",
            extra_trigger: ".breadcrumb",
            run: function () {}
        },
        {
            content: 'click first item',
            trigger: ".o_list_view .o_data_row",
            run: 'click'
        },
        {
            content: 'click trust ball',
            trigger: '#trustDropdown',
            run: 'click'
        },
        {
            content: 'change trust',
            trigger: '.o_change_trust[data-new-trust="good"]',
            run: 'click'
        },
        {
            content: 'send by mail',
            trigger: '.o_ohada_reports_followup_send_mail_button',
            run: 'click'
        },
        {
            content: 'check that message telling that mail has been sent is shown',
            trigger: '.alert:contains(The follow-up report was successfully emailed!)',
            run: function () {}
        },
        {
            content: 'dismiss alert',
            trigger: '.alert .close',
            run: 'click'
        },
        {
            content: 'Click the Do it later button',
            trigger: '.o_ohada_reports_followup_do_it_later_button',
            run: 'click'
        },
     ]
);

});
