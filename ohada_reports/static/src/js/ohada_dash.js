odoo.define('ohada_dash.Dash', function (require) {
    "use strict";

    var Class = require('web.Class');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc')
    var session = require('web.session');
    var KanbanController = require('web.KanbanController');
    var AbstractAction = require("web.AbstractAction");
    var ControlPanelMixin = require('web.ControlPanelMixin');
    
    var action = new AbstractAction(ControlPanelMixin);
    var includeDict = {
        renderButtons: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (this.modelName === "ohada.dash") {
                this.$buttons.on('click', '.o_call_wizard', function () {
                    rpc.query({
                        model: "ohada.dash",
                        method: "open_wizard",
                        args: [{}]
                    }).then(function(result) {
                        self.do_action(result);
                    });
                });
                this.$buttons.find('.o-kanban-button-new')[0].hidden = true
                this.$buttons.find('.o_button_import')[0].hidden = true
            }
        }
    };
    KanbanController.include(includeDict);
});
