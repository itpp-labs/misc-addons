/******************************************************************************
*
*    Copyright (C) 2014-2015 Augustin Cisterne-Kaas (ACK Consulting Limited)
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU General Public License for more details.
*
*    You should have received a copy of the GNU General Public License
*    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
******************************************************************************/
odoo.define('web_polymorphic_field.FieldPolymorphic', function (require) {
    var fieldRegistry = require('web.field_registry');
    var registry_selection = require('web.field_registry').get('selection');

    var FieldPolymorphic = registry_selection.extend( {
        init: function(parent, name, record, options) {
            this._super(parent, name, record, options);
            this.polymorphic = this.attrs.polymorphic;
        },
        add_polymorphism: function() {
            if(this.value != false) {
                var allFieldWidgets = this.getParent().allFieldWidgets;
                // allFieldWidgets is an object which contains single element
                // which contains fields inside. So, take first element
                var fields = allFieldWidgets[Object.keys(allFieldWidgets)[0]];

                var polymorphic = this.polymorphic;
                var polymorphic_field = _.find(fields, function(x){return x.name==polymorphic});
                polymorphic_field.relation = this.value;
            }
        },
        _render: function() {
            this._super();
            this.add_polymorphism();
        },
        store_dom_value: function (e) {
            this._super();
            this.add_polymorphism();
        }
    });
    fieldRegistry.add('polymorphic', FieldPolymorphic);
});
