
odoo.define('web_debranding.field_upgrade', function (require) {
"use strict";

    var core = require('web.core');
    var UpgradeBoolean = core.form_widget_registry.get('upgrade_boolean');
    var UpgradeRadio = core.form_widget_registry.get('upgrade_radio');

    var include = {
        'start': function(){
            var $el = this.$el;
            var i = 1;
            var MAX = 10;
            while (true){
                if (i > MAX)
                    break;
                i++;
                if ($el.prop("tagName") == 'TR'){
                    $el.hide();
                    break;
                }
                $el = $el.parent();
                if (!$el)
                    break;
            }
        },
        'on_click_input':function(){
        }
    };

    //skip this for a while as we don't have example to test it
    //UpgradeRadio.include(include);
    if (UpgradeBoolean.prototype.template != 'FieldUpgradeBoolean'){
        // we are on enterprise. No need to update
        return;
    }

    UpgradeBoolean.include(include);
});
