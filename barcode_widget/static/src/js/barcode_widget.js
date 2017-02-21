odoo.define('barcode_widget.form_widgets', function (require) {
    "use strict";

    var core = require('web.core');
    var form_common = require('web.form_common');
    var FieldChar = core.form_widget_registry.get('char');

    var Barcode128Widget = FieldChar.extend({
        template: 'Barcode128Widget',
        render_value: function () {
            var show_value = this.format_value(this.get('value'), '');
            if (this.$input) {
                this.$input.val(show_value);
            }else{
                this.$el.find('span').text(show_value);
                var barcode_path = '/report/barcode/Code128/' + show_value +'?width=250&height=50';
                var $barcodelink = this.$el.find('a');
                $barcodelink.attr("href", barcode_path);
                var $barcode = this.$el.find('img');
                $barcode.attr("src", barcode_path);
            }
        }
    });
    core.form_widget_registry.add('BarCode128', Barcode128Widget);
});
