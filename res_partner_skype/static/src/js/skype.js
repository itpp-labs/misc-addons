(function() {

var instance = openerp;
var _t = instance.web._t,
   _lt = instance.web._lt;
var QWeb = instance.web.qweb;

instance.web.form.FieldSkype = instance.web.form.FieldChar.extend({
    template: 'FieldSkype',
    initialize_content: function() {
        this._super();
        var $button = this.$el.find('button');
        $button.click(this.on_button_clicked);
        this.setupFocus($button);
    },
    render_value: function() {
        if (!this.get("effective_readonly")) {
            this._super();
        } else {
            this.$el.find('a')
                    .attr('href', this.skype_uri())
                    .text(this.get('value') || '');
        }
    },
    skype_uri:function(){
        //http://developer.skype.com/skype-uris/reference
        return 'skype:' + this.get('value') + '?'+(this.options.type || 'chat') + (this.options.video?'&video=true':'') + (this.options.topic?'&topic='+encodeURIComponent(this.options.topic):'');
    },
    on_button_clicked: function() {
        if (!this.get('value') || !this.is_syntax_valid()) {
            this.do_warn(_t("Skype Error"), _t("Can't skype to invalid skype address"));
        } else {
            location.href = this.skype_uri();
        }
    }
});

instance.web.form.widgets.add('skype', 'instance.web.form.FieldSkype');
})();
