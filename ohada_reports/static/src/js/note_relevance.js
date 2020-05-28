odoo.define('custom_project.web_export_view', function (require) {

"use strict";
var core = require('web.core');
var ListView = require('web.ListView');
var ListController = require("web.ListController");

var includeDict = {
    renderButtons: function () {
        this._super.apply(this, arguments);
        if (this.modelName === "note.relevance") {
            var your_btn = this.$buttons.find('button.o_button_set_relevance')
            your_btn.on('click', this.proxy('o_button_set_relevance'))
        }
    },
    o_button_set_relevance: function(){
        var self = this;
        var state = self.model.get(self.handle, {raw: true});
        var def1 = this._rpc({
                model: 'note.relevance',
                method: 'update_note_relevance',
                args: [{}],
        }).done(function(result) {
            self.data =  result;
        });
        return $.when(def1);
    }
};
ListController.include(includeDict);
});