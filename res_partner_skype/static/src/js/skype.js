(function() {

var instance = openerp;
var _t = instance.web._t,
   _lt = instance.web._lt;
var QWeb = instance.web.qweb;

instance.web.form.FieldSkype = instance.web.form.FieldChar.extend({
    template: 'FieldSkype',
    prefix: 'skype',
    init: function() {
        this._super.apply(this, arguments);
        this.clickable = true;
    },
    render_value: function() {
        this._super();
        if (this.get("effective_readonly") && this.clickable) {
            this.$el.attr('href', this.prefix + ':' + this.get('value') + '?'+(this.options.type || 'call'));
        }
    }
});

instance.web.form.widgets.add('skype', 'instance.web.form.FieldSkype');
})();
