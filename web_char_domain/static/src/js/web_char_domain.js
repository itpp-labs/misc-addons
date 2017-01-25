openerp.web_char_domain = function(instance){
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.web.form.FieldCharDomain.include({
        display_field: function(){
            this._super();
            var domain = 'None';
            if (this.get('value')){
                domain = instance.web.pyeval.eval('domain', this.get('value'));
            }
            this.$('.oe_domain_value').text(JSON.stringify(domain));
        }
    });
};
