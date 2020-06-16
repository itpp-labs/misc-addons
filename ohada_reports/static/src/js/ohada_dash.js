odoo.define('ohada_dash.Dash', function (require) {
    "use strict";

    var Class = require('web.Class');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc')    

    var Dash = Class.extend({
        init: function(){
            setTimeout(init_after_qweb_render, 2000);
        },
    });

    function init_after_qweb_render(){
        $('.o_cp_searchview').empty();
        $('.o_cp_right').empty();
        // $('.o_control_panel').append(QWeb.render('', {widget: this}));
        // $(".note").click(function () {
        //     // console.log("qw");
        //     rpc.query({
        //         model: 'ohada.dash',
        //         method: 'open_action_for_notes',
        //         args: [{
        //             'shortname': this.innerText,
        //         }]
        //     }).then(function (result) {            
        //         console.log(result);
        //     });
        // });
    }

    var d = new Dash();

    return Dash;
});
