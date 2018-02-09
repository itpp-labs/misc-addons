odoo.define('web_debranding.field_upgrade', function (require) {
"use strict";

    var field_registry = require('web.field_registry');
    /*
      Following line doesn't work in enterprise, because web_enterprise module
      removes web/.../upgrade_fieds.js files from backend assets and adds with new
      module web_enterprise.upgrade_widgets

      For this reason you can see following output in browser console in Enterprise:

      warning: Some modules could not be started
      Missing dependencies:    ["web.upgrade_widgets"]
      Non loaded modules:      ["web_debranding.field_upgrade"]
    */
    require('web.upgrade_widgets');
    var UpgradeBoolean = field_registry.get('upgrade_boolean');
    var UpgradeRadio = field_registry.get('upgrade_radio');

    if (!UpgradeBoolean){
        // we are on enterprise. No need to update
        return;
    }

    var include = {
        _render: function () {
/*
  Remove following element:

 <div class="col-xs-12 col-md-6 o_setting_box" title="Boost your sales with two kinds of discount programs: promotions and coupon codes. Specific conditions can be set (products, customers, minimum purchase amount, period). Rewards can be discounts (% or amount) or free products.">
  <div class="o_setting_left_pane">
    <div class="o_field_boolean o_field_widget" name="module_sale_coupon">
   </div>
  </div>
<div class="o_setting_right_pane">
  <label class="o_form_label" for="o_field_input_18" data-original-title="" title="" aria-describedby="tooltip822540">Coupons &amp; Promotions
  </label>
  <div class="text-muted" id="sale_coupon">
                  Manage promotion &amp; coupon programs

  </div>
</div>
</div>

*/
            // this.$el is .o_field_boolean in example above
            this.$el.parent().parent().remove();
        }
    };

    UpgradeRadio.include(include);
    UpgradeBoolean.include(include);
});
