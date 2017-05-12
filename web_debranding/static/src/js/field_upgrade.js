odoo.define('web_debranding.field_upgrade', function (require) {
"use strict";

    var core = require('web.core');
    var UpgradeBoolean = core.form_widget_registry.get('upgrade_boolean');
    var UpgradeRadio = core.form_widget_registry.get('upgrade_radio');

    if (!UpgradeBoolean || UpgradeBoolean.prototype.template !== 'FieldUpgradeBoolean'){
        // we are on enterprise. No need to update
        return;
    }

    var include = {
        'start': function(){
            // $el = .oe_form_field
            var $el = this.$el;

            // $el = div
            $el = $el.parent();
            $el.hide();

            // $el = div
            $el = $el.parent();
            if (_.all($el.children(), function (ch) {
                        return $(ch).css('display') === 'none';
                        }
                    )
                ){
                // hide whole group as doesn't have fields
                for (var i=0; i<10; i++) {
                    if ($el.prop("tagName") === 'TR'){
                        $el.hide();
                        break;
                    }
                    $el = $el.parent();
                    if (!$el) {
                        break;
                    }
                }
            }
            return this._super.apply(this, arguments);
        },
        'on_click_input':function(){
            console.log('skip');
        }
    };

    //skip this for a while as we don't have example to test it
    //UpgradeRadio.include(include);
    UpgradeBoolean.include(include);
});
