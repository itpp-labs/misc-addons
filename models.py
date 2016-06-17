# -*- coding: utf-8 -*-

from openerp.osv import osv


class stock_picking(osv.osv):
    _name = "stock.picking"

    def process_barcode_from_ui(self):
        pass

    def get_next_picking_for_ui(self):
        pass

    def check_group_pack(self):
        pass

    def do_prepare_partial(self):
        pass

    def process_product_id_from_ui(self):
        pass

    def action_pack(self):
        pass

    def action_drop_down(self):
        pass

    def action_done_from_ui(self):
        pass

    def create_and_assign_lot(self):
        pass

    def action_print(self):
        pass

    def do_print_picking(self):
        pass
