/*  Copyright 2015-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    Copyright 2017 ArtyomLosev <https://github.com/ArtyomLosev>
    License MIT (https://opensource.org/licenses/MIT). */
odoo.define("web_debranding.base", function (require) {
    "use strict";
    var WebClient = require("web.WebClient");

    WebClient.include({
        init: function (parent) {
            this._super.apply(this, arguments);
            var self = this;
            this.set("title_part", {zopenerp: ""});
            odoo.debranding_new_name = "";
            odoo.debranding_new_website = "";
            odoo.debranding_new_title = "";

            self._rpc(
                {
                    model: "ir.config_parameter",
                    method: "get_debranding_parameters",
                },
                {
                    shadow: true,
                }
            ).then(function (result) {
                odoo.debranding_new_name = result["web_debranding.new_name"];
                odoo.debranding_new_website = result["web_debranding.new_website"];
                odoo.debranding_new_title = result["web_debranding.new_title"];
                self.set("title_part", {zopenerp: odoo.debranding_new_title});
            });
        },
    });
});
