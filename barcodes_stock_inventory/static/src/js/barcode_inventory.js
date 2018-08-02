/* Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

odoo.define('barcodes_stock_inventory', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var core = require('web.core');
    var ListView = require('web.ListView');
    var FormViewBarcodeHandler = require('barcodes.FormViewBarcodeHandler');
    var _t = core._t;
    var qweb = core.qweb;

    FormViewBarcodeHandler.include({
        start: function() {
            this._super();
            this.map_barcode_method['O-CMD.INV'] = _.bind(this.click_button_start_inventory, this);
//            this.map_barcode_method['O-CMD.CREATE'] = _.bind(this.click_button_create, this.form_view);
            this.map_barcode_method['O-CMD.DISCARD'] = _.bind(this.click_button_discard, this.form_view);
            // inside inventory

            this.map_barcode_method['O-CMD.VALID'] = _.bind(this.click_button_validate_inventory, this.form_view);
            this.map_barcode_method['O-CMD.CANCEL'] = _.bind(this.click_button_cancel_inventory, this.form_view);
            this.map_barcode_method['O-CMD.NEXT'] = _.bind(this.click_button_next_inventory, this.form_view);
            this.map_barcode_method['O-CMD.PREV'] = _.bind(this.click_button_previous_inventory, this.form_view);
        },

        click_button_start_inventory: function() {
            $('.o_content header button.btn.btn-sm.oe_highlight:contains("Start Inventory")').trigger('click');
        },
//        click_button_create: function() {
//            $('.o_cp_left .o_cp_buttons button.o_form_button_create:contains("Create")').trigger('click');
//        },
        click_button_discard: function() {
            $('.o_cp_buttons button.btn.btn-sm.o_form_button_cancel:contains("Discard")').trigger('click');
        },
        click_button_validate_inventory: function() {
            $('.o_content header button.btn.btn-sm.oe_highlight:contains("Validate Inventory")').trigger('click');
        },
        click_button_cancel_inventory: function() {
            $('.o_content header button.btn.btn-sm:contains("Cancel Inventory")').trigger('click');
        },
        click_button_next_inventory: function() {
            $('.o_cp_right .o_cp_pager button.fa-chevron-right.o_pager_next').trigger('click');
        },
        click_button_previous_inventory: function() {
            $('.o_cp_right .o_cp_pager button.fa-chevron-left.o_pager_previous').trigger('click');
        },

    });

});
