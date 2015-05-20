(function() {

var instance = openerp;
var _t = instance.web._t,
_lt = instance.web._lt;
var QWeb = instance.web.qweb;

instance.web.form.FieldVK = instance.web.form.FieldChar.extend({
    template: 'FieldVK',
    render_value: function() {
        if (!this.get("effective_readonly")) {
            this._super();
        } 
        else {
            value = this.get('value');
            this.$el.find('a')
                    .attr('href', value)
                    .text(value || '');
        }
    },
});

instance.web.form.widgets.add('vk', 'instance.web.form.FieldVK');
})()
