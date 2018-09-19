odoo.define('base_details', function(require) {
    'use strict';

    var FieldReference = require('web.relational_fields').FieldReference;

    FieldReference.include({
        _reset: function () {
            this._super.apply(this, arguments);
            // due to odoo client error we've redefined this method to be able to change reference field values after it was set in onchange method src: https://github.com/odoo/odoo/pull/27109
            this._setState();
        },
    });

});
