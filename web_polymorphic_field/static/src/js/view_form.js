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

    var FieldSelection = core.form_widget_registry.get('selection');
    var FieldPolymorphic = FieldSelection.extend( {
        template: "FieldSelection",
        init: function(field_manager, node) {
            this._super(field_manager, node);
            this.polymorphic = this.node.attrs.polymorphic;
        },
        add_polymorphism: function(reinit) {
            if(this.get_value() != false) {
                polymorphic_field = this.field_manager.fields[this.polymorphic];
                polymorphic_field.field.relation = this.get_value();
            }
        },
        render_value: function() {
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
