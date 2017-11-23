odoo.define('web_debranding.dashboard', function (require) {
"use strict";

    var dashboard = require('web_settings_dashboard');
    dashboard.Dashboard.include({
        start: function(){
            this.all_dashboards = _.without(this.all_dashboards, 'share');

            // remove Share section completly
            this.$('.o_web_settings_dashboard_share').parent().remove();

            var self = this;
            return this._super().then(function(){
                // Remove bottom of Apps settion (links to odoo apps store)
                self.$('.o_browse_apps').parent().nextAll().remove();


                // Following code removes <hr/>, text node and <a/>
                /*
                  <div class="row o_web_settings_dashboard_planners_list">
                  ...
                  </div>
                  <hr/>
                  Need more help? <a target="_blank" href="https://www.odoo.com/documentation/user">Browse the documentation.</a>
                */
                var $all = self.$('.o_web_settings_dashboard_planners_list').nextAll();
                var text_node = $all[0].nextSibling;
                if (text_node.remove){
                    text_node.remove();
                    $all.remove();
                } else {
                    // old browser - hide whole block
                    self.$('.o_web_settings_dashboard_planner').parent().remove();
                }
            });
        },
    });
});
