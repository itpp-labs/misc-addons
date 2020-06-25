odoo.define('service.service_team_dashboard', function (require) {
"use strict";

var core = require('web.core');
var formats = require('web.field_utils');
var field_utils = require('web.field_utils');
var rpc = require('web.rpc');
var session = require('web.session');
var KanbanView = require('web.KanbanView');
var BasicView = require('web.BasicView');
var config = require('web.config');
var KanbanModel = require('web.KanbanModel');
var KanbanRenderer = require('web.KanbanRenderer');
var KanbanController = require('web.KanbanController');
var utils = require('web.utils');
var view_registry=require('web.view_registry');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var ServiceTeamDashboardRendererView = KanbanRenderer.extend({
    events: _.extend({}, KanbanRenderer.prototype.events, {
        'click .o_dashboard_action': 'on_dashboard_action_clicked',
        'click .o_target_to_set': 'on_dashboard_target_clicked',
    }),


    _render: function() {
        var super_render = this._super;
        var self = this;

        return this.fetch_data().then(function(result){
            self.show_demo = result && result.nb_opportunities === 0;
            
            var sales_dashboard = QWeb.render('service.Dashboard', {
                widget: self,
                show_demo: self.show_demo,
                values: result,
            });
            super_render.call(self);
            $(sales_dashboard).prependTo(self.$el);


        });
    },


    fetch_data: function() {
        return $.when(this._rpc({
                    model: 'service_drm.dashboard',
                    method: 'compute_count_all',
                    args: [],
                }));
    },

    on_dashboard_action_clicked: function(ev){
        ev.preventDefault();

        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_extra = $action.data('extra');
        var additional_context = {};

        // TODO: find a better way to add defaults to search view
        if (action_name === 'service.service_action') {
            additional_context.search_default_mymeetings = 1;
        } else if (action_name === 'crm.crm_lead_action_activities') {
            if (action_extra === 'today') {
                additional_context.search_default_today = 1;
            } else if (action_extra === 'this_week') {
                additional_context.search_default_this_week = 1;
            } else if (action_extra === 'overdue') {
                additional_context.search_default_overdue = 1;
            }
        } else if (action_name === 'crm.action_your_pipeline') {
            if (action_extra === 'overdue') {
                additional_context['search_default_overdue'] = 1;
            } else if (action_extra === 'overdue_opp') {
                additional_context['search_default_overdue_opp'] = 1;
            }
        } else if (action_name === 'crm.crm_opportunity_report_action_graph') {
            additional_context.search_default_won = 1;
        }

        this.do_action(action_name, {additional_context: additional_context});
    },

    on_dashboard_target_clicked: function(ev){
        if (this.show_demo) {
            // The user is not allowed to modify the targets in demo mode
            return;
        }

        var self = this;
        var $target = $(ev.currentTarget);
        var target_name = $target.attr('name');
        var target_value = $target.attr('value');

        var $input = $('<input/>', {type: "text"});
        $input.attr('name', target_name);
        if (target_value) {
            $input.attr('value', target_value);
        }
        $input.on('keyup input', function(e) {
            if(e.which === $.ui.keyCode.ENTER) {
                self.on_change_input_target(e);
            }
        });
        $input.on('blur', function(e) {
            self.on_change_input_target(e);
        });

        $.when(this._updated).then(function() {
            $input.replaceAll(self.$('.o_target_to_set[name=' + target_name + ']')) // the target may have changed (re-rendering)
                  .focus()
                  .select();
        });
    },

    _render_monetary_field: function(value, currency_id) {
        var currency = session.get_currency(currency_id);
        var digits_precision = currency && currency.digits;
        value = formats.formatMonetary(value || 0, {type: "float", digits: digits_precision});
        if (currency) {
            if (currency.position === "after") {
                value += currency.symbol;
            } else {
                value = currency.symbol + value;
            }
        }
        return value;
    },
});
    



var ServiceTeamDashboardModel = KanbanModel.extend({



})

var ServiceTeamDashboardController = KanbanController.extend({
    /* The company_button_action action allows the buttons of the setup bar to
    * trigger Python code defined in api.model functions in res.company model,
    * and to execute the action returned them.
    * It uses the 'type' attributes on buttons : if 'company_object', it will
    * run Python function 'name' of company model.
    */
    custom_events: _.extend({}, KanbanController.prototype.custom_events, {
        // dashboard_open_action: '_onDashboardOpenAction',
        // company_button_action: '_triggerCompanyButtonAction',
    }),

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {OdooEvent} e
     */
    // _onDashboardOpenAction: function (e) {
    //     var action_name = e.data.action_name;
    //     var action_context = e.data.action_context;
    //     return this.do_action(action_name, {
    //         additional_context: action_context,
    //     });
    // },

    /**
    * Manages the clicks on the setup bar buttons.
    **/
    // _triggerCompanyButtonAction: function (odooEvent) {
    //     var self = this
    //     if (odooEvent.data.rpc_method !== undefined) {
    //         self._rpc({
    //                 model: 'res.company',
    //                 method: odooEvent.data.rpc_method,
    //                 args: [],
    //             })
    //             .then(
    //                 function(rslt_action) {
    //                     if (rslt_action !== undefined) {
    //                         self.do_action(rslt_action, {
    //                             action_context: odooEvent.data.context,
    //                             on_close: function () {
    //                                 self.trigger_up('reload'); //Reloads the dashboard to refresh the status of the setup bar.
    //                             },
    //                         });
    //                     }
    //                     else { //Happens for any button not returning anything, like the cross to close the setup bar, for example.
    //                         self.trigger_up('reload');
    //                     }
    //                 });
    //     }
    // }
});


var ServiceTeamDashboardView = KanbanView.extend({
    config: _.extend({}, KanbanView.prototype.config, {
        // Model: ServiceTeamDashboardModel,
        Renderer: ServiceTeamDashboardRendererView,
        // Controller: ServiceTeamDashboardController,
    }),
    display_name: _lt('Dashboard'),
    icon: 'fa-dashboard',
    searchview_hidden: true,
});

view_registry.add('service_team_dashboard', ServiceTeamDashboardView);

return {
    // Model: ServiceTeamDashboardModel,
    Renderer: ServiceTeamDashboardRendererView,
    // Controller: ServiceTeamDashboardController,
};

});

