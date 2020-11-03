odoo.define('theme_kit.model', function (require) {
    "use strict";

    var WebClient = require("web.WebClient");

    WebClient.include({
        init: function (parent) {
            this._super.apply(this, arguments);
            var self = this;
        },
    });
    $(document).ready(function(e){
        $('#odooMenuBarNav > div > div.o_sub_menu_content > ul > li > a').click(function (e) {
            if($('#odooMenuBarNav > div > div.o_sub_menu_content > ul > li > a') != undefined){
                $('#odooMenuBarNav > div > div.o_sub_menu_content > ul > li > a').removeClass("active");
                $("#odooMenuBarNav > div > div.o_sub_menu_content > ul > li.active").removeClass("active")
            }
            $(e.target).addClass("active");
        });
        $("#sidebar > li > a").click(function(e){
            if($("#sidebar > li > a") != undefined){
                $("#sidebar > li > a").removeClass("active");
            }
            $(e.target).addClass("active");
        });
    });
});