/*  Copyright 2014 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    Copyright 2016 x620 <https://github.com/x620>
    Copyright 2017 Ilmir Karamov <https://it-projects.info/team/ilmir-k>
    Copyright 2017 ArtyomLosev <https://github.com/ArtyomLosev>
    Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
    License MIT (https://opensource.org/licenses/MIT). */
odoo.define("res_partner_skype.widget", function(require) {
    "use strict";

    var fieldRegistry = require("web.field_registry");
    var basicFields = require("web.basic_fields");
    var FieldEmail = basicFields.FieldEmail;

    var FieldSkype = FieldEmail.extend({
        description: "skype",
        prefix: "skype",

        _renderReadonly: function() {
            this.$el
                .text(this.value)
                .addClass("o_form_uri o_text_overflow")
                .attr("href", this.prefix + ":" + this.value + "?call");
        },
    });

    fieldRegistry.add("skype", FieldSkype);
});
