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
openerp.web_polymorphic_field = function (instance) {
    instance.web.form.FieldPolymorphic = instance.web.form.FieldSelection.extend( {
        template: "FieldSelection",
        events: {
            'change select': 'store_dom_value'
        },
        init: function(field_manager, node) {
            this._super(field_manager, node);
            this.polymorphic = this.node.attrs.polymorphic;
        },
        add_polymorphism: function() {
            if(this.get_value() != false) {
                polymorphic_field = this.field_manager.fields[this.polymorphic];
                polymorphic_field.field.relation = this.get_value();
            }
        },
        render_value: function() {
            this._super();
            this.add_polymorphism(); 
        },
        store_dom_value: function () {
            this._super();
            this.add_polymorphism(); 
        }
    });
    instance.web.form.widgets.add('polymorphic', 'instance.web.form.FieldPolymorphic');
};
