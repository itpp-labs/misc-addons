odoo.define('ohada_reports.ActionManager', function (require) {
"use strict";

/**
 * The purpose of this file is to add the support of Odoo actions of type
 * 'ir_actions_account_report_download' to the ActionManager.
 */

var ActionManager = require('web.ActionManager');
var crash_manager = require('web.crash_manager');
var framework = require('web.framework');
var session = require('web.session');

ActionManager.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Executes actions of type 'ir_actions_account_report_download'.
     *
     * @private
     * @param {Object} action the description of the action to execute
     * @returns {Deferred} resolved when the report has been downloaded ;
     *   rejected if an error occurred during the report generation
     */
    _executeAccountReportDownloadAction: function (action) {
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/ohada_reports',
            data: action.data,
            success: def.resolve.bind(def),
            error: function () {
                crash_manager.rpc_error.apply(crash_manager, arguments);
                def.reject();
            },
            complete: framework.unblockUI,
        });
        return def;
    },
    /**
     * Overrides to handle the 'ir_actions_account_report_download' actions.
     *
     * @override
     * @private
     */
    _handleAction: function (action, options) {
        if (action.type === 'ir_actions_account_report_download') {
            return this._executeAccountReportDownloadAction(action, options);
        }
        return this._super.apply(this, arguments);
    },
});

});
