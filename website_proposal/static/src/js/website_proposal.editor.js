(function(){
    var instance = openerp;
    var QWeb = instance.qweb;
    var _t = instance._t;
    instance.website.RTE.include({
        start_edition: function(){
            var def = this._super.apply(this, arguments);
            def.then(function(){
                $("[forced-contenteditable=false]").attr('contenteditable', false);
            })
            return def;
        }
    })

})()