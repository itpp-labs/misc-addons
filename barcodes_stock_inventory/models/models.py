# -*- coding: utf-8 -*-
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class BarcodeStockInventory(models.Model):

    _name = 'stock.inventory'
    _inherit = ['stock.inventory', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):

        location = self.env['stock.location'].search([('barcode', '=', barcode)])
        if location:
            self.location_id = location[0]
            return

        product = self.env['product.product'].search([('barcode', '=', barcode)])[0]
        if not product:
            return

        line = False
        lines = self.line_ids.filtered(lambda ln: ln.product_id.id == product.id)
        if len(lines) == 1:
            line = lines
        if len(lines) > 1:
            for ln in lines:
                if ln.location_id.id is self.location_id.id:
                    line = ln
        if line:
            line['product_qty'] += 1
        else:
            line = {
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'location_id': self.location_id.id,
                'product_qty': 1,
            }
            self.line_ids += self.env['stock.inventory.line'].new(line)
