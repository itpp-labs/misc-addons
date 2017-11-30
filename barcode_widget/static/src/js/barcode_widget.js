openerp.barcode_widget = function(instance){
    "use strict";
    var FieldChar = instance.web.form.FieldChar
    openerp.web.form.widgets.add('BarCode128', 'openerp.web.form.BarCode128');
    openerp.web.form.BarCode128 = FieldChar.extend({
        render_value: function() {
            var show_value = this.format_value(this.get('value'), '');
            var barcode_path = '/report/barcode/?type=Code128&value=' + show_value +'&width=250&height=50';
            var $barcode = this.$el.find('img');
            $barcode.attr('src', barcode_path)
        },
        init: function(){
            console.log('format value')
        }
    });

}
