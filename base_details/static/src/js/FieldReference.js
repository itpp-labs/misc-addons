odoo.define('base_details', function(require) {
    'use strict';

    var FieldReference = require('web.relational_fields').FieldReference;

    FieldReference.include({
        _reset: function () {
            this._super.apply(this, arguments);
            this._setState();
        },
    });

});
