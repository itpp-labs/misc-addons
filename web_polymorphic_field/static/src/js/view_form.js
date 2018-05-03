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
    var core = require('web.core');
//    var basic_fields = require('web.basic_fields');
    var registry_selection = require('web.field_registry').get('selection');
    var registry_many2one = require('web.field_registry').get('many2one');
//    var FieldSelection = core.form_widget_registry.get('selection')
    var relational_fields = require('web.relational_fields')


//    var search_super = registry_many2one.prototype._search;
//    registry_many2one.include({
//        _search: function(args){
//            console.log('sdfsdf')
//            if (this.field.type === "integer"){
//                this.record.data['model']
//            }
//            return search_super(args);
//        }
//    });

    var FieldPolymorphic = registry_selection.include( {
        init: function(parent, name, record, options) {
            this._super(parent, name, record, options);
            this.polymorphic = this.attrs.polymorphic;
        },
        add_polymorphism: function() {
            if(this.value != false) {
                var polymorphic_field = this.record.fields[this.polymorphic];
                if (polymorphic_field && this.value){
                    polymorphic_field.relation = this.value;
                }
//                this.record.fields[this.polymorphic].relation = this.value;
                console.log(this.record.fields[this.polymorphic])
                console.log(this.record.fields[this.polymorphic])
                console.log(registry_selection)
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
    core.form_widget_registry.add('polymorphic', FieldPolymorphic);
});
