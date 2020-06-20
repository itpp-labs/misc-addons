odoo.define('ohada_dash.Dash', function (require) {
    "use strict";

    var Class = require('web.Class');
    var core = require('web.core');
    var QWeb = core.qweb;
    var session = require('web.session');

    var Dash = Class.extend({
        init: function(){
            setTimeout(check_buttons_rendered, 500);
        },
    });

    function check_buttons_rendered(){
        if($(".export").text()){
            $(".export").click(function () {
                session.rpc('/get_report_values', {
                }).then(function (result) {
                    console.log(result);
                });
            });
        }
        else{
            setTimeout(check_buttons_rendered, 500);
        }
    }

    var d = new Dash();

    return Dash;
});
