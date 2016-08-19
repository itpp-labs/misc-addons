openerp.web_logo = function(instance){
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.web.UserMenu.include({


    do_update: function () {
        this._super.apply(this, arguments);
        var self = this;
        var fct = function() {
            if (!self.session.uid)
                return;
            var func = new instance.web.Model("res.users").get_func("read");
            return self.alive(func(self.session.uid, ["name", "company_id"])).then(function(res) {
                $('.oe_logo img').attr('src', '/web/binary/company_logo?company_id=' + res.company_id[0]);
            });
        };
        this.update_promise = this.update_promise.then(fct, fct);
    }


    });

};
