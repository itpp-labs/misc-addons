odoo.define('theme_kit.model', function (require) {
    "use strict";

    function add_active_class_top_panel(elem)
    {
        if($('#odooMenuBarNav > div > div.o_sub_menu_content > ul > li > a') != undefined){
            $('#odooMenuBarNav > div > div.o_sub_menu_content > ul > li > a').removeClass("active");
            $("#odooMenuBarNav > div > div.o_sub_menu_content > ul > li.active").removeClass("active")
        }
        if(localStorage.getItem($(elem).text().replace(/\s/g, '')))
            localStorage.setItem($(elem).text().replace(/\s/g, ''), true);
        $(elem).addClass("active");
    }

    $(document).ready(function(){
        $('#odooMenuBarNav > div > div.o_sub_menu_content > ul > li > a').click(function (e) {
            add_active_class_top_panel(this);
        });
        $("#sidebar > li > a").click(function(e){
            if($("#sidebar > li > a") != undefined){
                $("#sidebar > li > a").removeClass("active");
            }
            $(this).addClass("active");
        });
        $("#odooMenuBarNav > div > div > ul > li > ul > li").click(function(e){
            $(this.parentElement.parentElement.childNodes).each(function(){
                if($(this).hasClass("dropdown-toggle"))
                    setTimeout(add_active_class_top_panel, 10, this);
            });
        });
    });
});