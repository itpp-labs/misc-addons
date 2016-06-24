# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp import SUPERUSER_ID, api
from openerp.tools.float_utils import float_compare


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def process_barcode_from_ui(self, cr, uid, picking_id, barcode_str, visible_op_ids, context=None):
        """This function is called each time there barcode scanner reads an input"""
        lot_obj = self.pool.get('stock.production.lot')
        package_obj = self.pool.get('stock.quant.package')
        product_obj = self.pool.get('product.product')
        stock_operation_obj = self.pool.get('stock.pack.operation')
        stock_location_obj = self.pool.get('stock.location')
        answer = {'filter_loc': False, 'operation_id': False}
        # check if the barcode correspond to a location
        matching_location_ids = stock_location_obj.search(cr, uid, [('barcode', '=', barcode_str)], context=context)
        if matching_location_ids:
            # if we have a location, return immediatly with the location name
            location = stock_location_obj.browse(cr, uid, matching_location_ids[0], context=None)
            answer['filter_loc'] = stock_location_obj._name_get(cr, uid, location, context=None)
            answer['filter_loc_id'] = matching_location_ids[0]
            return answer
        # check if the barcode correspond to a product
        matching_product_ids = product_obj.search(cr, uid, ['|', ('barcode', '=', barcode_str),
                                                            ('default_code', '=', barcode_str)], context=context)
        if matching_product_ids:
            op_id = stock_operation_obj._search_and_increment(
                cr,
                uid,
                picking_id,
                [('product_id', '=', matching_product_ids[0])],
                filter_visible=True,
                visible_op_ids=visible_op_ids,
                increment=True,
                context=context
            )
            answer['operation_id'] = op_id
            return answer
        # check if the barcode correspond to a lot
        matching_lot_ids = lot_obj.search(cr, uid, [('name', '=', barcode_str)], context=context)
        if matching_lot_ids:
            lot = lot_obj.browse(cr, uid, matching_lot_ids[0], context=context)
            op_id = stock_operation_obj._search_and_increment(
                cr,
                uid,
                picking_id,
                [('product_id', '=', lot.product_id.id), ('lot_id', '=', lot.id)],
                filter_visible=True,
                visible_op_ids=visible_op_ids,
                increment=True,
                context=context
            )
            answer['operation_id'] = op_id
            return answer
        # check if the barcode correspond to a package
        matching_package_ids = package_obj.search(cr, uid, [('name', '=', barcode_str)], context=context)
        if matching_package_ids:
            op_id = stock_operation_obj._search_and_increment(
                cr,
                uid,
                picking_id,
                [('package_id', '=', matching_package_ids[0])],
                filter_visible=True,
                visible_op_ids=visible_op_ids,
                increment=True,
                context=context
            )
            answer['operation_id'] = op_id
            return answer
        return answer

    def get_next_picking_for_ui(self, cr, uid, context=None):
        """ returns the next pickings to process. Used in the barcode scanner UI"""
        if context is None:
            context = {}
        domain = [('state', 'in', ('assigned', 'partially_available'))]
        if context.get('default_picking_type_id'):
            domain.append(('picking_type_id', '=', context['default_picking_type_id']))
        return self.search(cr, uid, domain, context=context)

    def check_group_lot(self, cr, uid, context=None):
        """ This function will return true if we have the setting to use lots activated. """
        return self.pool.get('res.users').has_group(cr, uid, 'stock.group_production_lot')

    def check_group_pack(self, cr, uid, context=None):
        """ This function will return true if we have the setting to use package activated. """
        return self.pool.get('res.users').has_group(cr, uid, 'stock.group_tracking_lot')

    def action_assign_owner(self, cr, uid, ids, context=None):
        for picking in self.browse(cr, uid, ids, context=context):
            packop_ids = [op.id for op in picking.pack_operation_ids]
            self.pool.get('stock.pack.operation').write(cr, uid, packop_ids, {'owner_id': picking.owner_id.id}, context=context)

    @api.cr_uid_ids_context
    def do_prepare_partial(self, cr, uid, picking_ids, context=None):
        context = context or {}
        pack_operation_obj = self.pool.get('stock.pack.operation')
        # used to avoid recomputing the remaining quantities at each new pack operation created
        ctx = context.copy()
        ctx['no_recompute'] = True

        # get list of existing operations and delete them
        existing_package_ids = pack_operation_obj.search(cr, uid, [('picking_id', 'in', picking_ids)], context=context)
        if existing_package_ids:
            pack_operation_obj.unlink(cr, uid, existing_package_ids, context)
        for picking in self.browse(cr, uid, picking_ids, context=context):
            forced_qties = {}  # Quantity remaining after calculating reserved quants
            picking_quants = []
            # Calculate packages, reserved quants, qtys of this picking's moves
            for move in picking.move_lines:
                if move.state not in ('assigned', 'confirmed', 'waiting'):
                    continue
                move_quants = move.reserved_quant_ids
                picking_quants += move_quants
                forced_qty = (move.state == 'assigned') and move.product_qty - sum([x.qty for x in move_quants]) or 0
                # if we used force_assign() on the move, or if the move is incoming, forced_qty > 0
                if float_compare(forced_qty, 0, precision_rounding=move.product_id.uom_id.rounding) > 0:
                    if forced_qties.get(move.product_id):
                        forced_qties[move.product_id] += forced_qty
                    else:
                        forced_qties[move.product_id] = forced_qty
            for vals in self._prepare_pack_ops(cr, uid, picking, picking_quants, forced_qties, context=context):
                pack_operation_obj.create(cr, uid, vals, context=ctx)
        # recompute the remaining quantities all at once
        self.do_recompute_remaining_quantities(cr, uid, picking_ids, context=context)
        self.write(cr, uid, picking_ids, {'recompute_pack_op': False}, context=context)

    def process_product_id_from_ui(self, cr, uid, picking_id, product_id, op_id, increment=True, context=None):
        return self.pool.get('stock.pack.operation')._search_and_increment(
            cr,
            uid,
            picking_id,
            [('product_id', '=', product_id), ('id', '=', op_id)],
            increment=increment,
            context=context
        )

    @api.cr_uid_ids_context
    def action_pack(self, cr, uid, picking_ids, operation_filter_ids=None, context=None):
        """ Create a package with the current pack_operation_ids of the picking that aren't yet in a pack.
        Used in the barcode scanner UI and the normal interface as well.
        operation_filter_ids is used by barcode scanner interface to specify a subset of operation to pack"""
        if operation_filter_ids == None:
            operation_filter_ids = []
        stock_operation_obj = self.pool.get('stock.pack.operation')
        package_obj = self.pool.get('stock.quant.package')
        stock_move_obj = self.pool.get('stock.move')
        package_id = False
        for picking_id in picking_ids:
            operation_search_domain = [('picking_id', '=', picking_id), ('result_package_id', '=', False)]
            if operation_filter_ids != []:
                operation_search_domain.append(('id', 'in', operation_filter_ids))
            operation_ids = stock_operation_obj.search(cr, uid, operation_search_domain, context=context)
            pack_operation_ids = []
            if operation_ids:
                for operation in stock_operation_obj.browse(cr, uid, operation_ids, context=context):
                    # If we haven't done all qty in operation, we have to split into 2 operation
                    op = operation
                    if (operation.qty_done < operation.product_qty):
                        new_operation = stock_operation_obj.copy(
                            cr,
                            uid,
                            operation.id,
                            {'product_qty': operation.qty_done, 'qty_done': operation.qty_done},
                            context=context
                        )
                        stock_operation_obj.write(
                            cr,
                            uid,
                            operation.id,
                            {'product_qty': operation.product_qty - operation.qty_done, 'qty_done': 0},
                            context=context
                        )
                        op = stock_operation_obj.browse(cr, uid, new_operation, context=context)
                    pack_operation_ids.append(op.id)
                    if op.product_id and op.location_id and op.location_dest_id:
                        stock_move_obj.check_tracking_product(
                            cr,
                            uid,
                            op.product_id,
                            op.lot_id.id,
                            op.location_id,
                            op.location_dest_id,
                            context=context
                        )
                package_id = package_obj.create(cr, uid, {}, context=context)
                stock_operation_obj.write(
                    cr,
                    uid,
                    pack_operation_ids,
                    {'result_package_id': package_id},
                    context=context
                )
        return package_id

    def action_done_from_ui(self, cr, uid, picking_id, context=None):
        """ called when button 'done' is pushed in the barcode scanner UI """
        # write qty_done into field product_qty for every package_operation before doing the transfer
        pack_op_obj = self.pool.get('stock.pack.operation')
        for operation in self.browse(cr, uid, picking_id, context=context).pack_operation_ids:
            pack_op_obj.write(cr, uid, operation.id, {'product_qty': operation.qty_done},
                              context=dict(context, no_recompute=True))
        self.do_transfer(cr, uid, [picking_id], context=context)
        # return id of next picking to work on
        return self.get_next_picking_for_ui(cr, uid, context=context)

    def unpack(self, cr, uid, ids, context=None):
        quant_obj = self.pool.get('stock.quant')
        for package in self.browse(cr, uid, ids, context=context):
            quant_ids = [quant.id for quant in package.quant_ids]
            quant_obj.write(cr, SUPERUSER_ID, quant_ids, {'package_id': package.parent_id.id or False}, context=context)
            children_package_ids = [child_package.id for child_package in package.children_ids]
            self.write(cr, uid, children_package_ids, {'parent_id': package.parent_id.id or False}, context=context)
        # delete current package since it contains nothing anymore
        self.unlink(cr, uid, ids, context=context)
        return self.pool.get('ir.actions.act_window').for_xml_id(
            cr,
            uid,
            'stock',
            'action_package_view',
            context=context
        )

    @api.cr_uid_ids_context
    def open_barcode_interface(self, cr, uid, picking_ids, context=None):
        final_url = "/barcode/web/#action=stock.ui&picking_id=" + str(picking_ids[0])
        return {'type': 'ir.actions.act_url', 'url': final_url, 'target': 'self',}

    @api.cr_uid_ids_context
    def do_partial_open_barcode(self, cr, uid, picking_ids, context=None):
        self.do_prepare_partial(cr, uid, picking_ids, context=context)
        return self.open_barcode_interface(cr, uid, picking_ids, context=context)


class stock_picking_type(osv.osv):
    _inherit = "stock.picking.type"

    def open_barcode_interface(self, cr, uid, ids, context=None):
        final_url = "/barcode/web/#action=stock.ui&picking_type_id=" + str(ids[0]) if len(ids) else '0'
        return {'type': 'ir.actions.act_url', 'url': final_url, 'target': 'self'}


class stock_pack_operation(osv.osv):
    _inherit = "stock.pack.operation"

    def _search_and_increment(self, cr, uid, picking_id, domain, filter_visible=False, visible_op_ids=False, increment=True, context=None):
        """Search for an operation with given 'domain' in a picking, if it exists increment the qty (+1) otherwise create it

        :param domain: list of tuple directly reusable as a domain
        context can receive a key 'current_package_id' with the package to consider for this operation
        returns True
        """
        if context is None:
            context = {}

        # if current_package_id is given in the context, we increase the number of items in this package
        package_clause = [('result_package_id', '=', context.get('current_package_id', False))]
        existing_operation_ids = self.search(cr, uid, [('picking_id', '=', picking_id)] + domain + package_clause,
                                             context=context)
        todo_operation_ids = []
        if existing_operation_ids:
            if filter_visible:
                todo_operation_ids = [val for val in existing_operation_ids if val in visible_op_ids]
            else:
                todo_operation_ids = existing_operation_ids
        if todo_operation_ids:
            # existing operation found for the given domain and picking => increment its quantity
            operation_id = todo_operation_ids[0]
            op_obj = self.browse(cr, uid, operation_id, context=context)
            qty = op_obj.qty_done
            if increment:
                qty += 1
            else:
                qty -= 1 if qty >= 1 else 0
                if qty == 0 and op_obj.product_qty == 0:
                    # we have a line with 0 qty set, so delete it
                    self.unlink(cr, uid, [operation_id], context=context)
                    return False
            self.write(cr, uid, [operation_id], {'qty_done': qty}, context=context)
        else:
            # no existing operation found for the given domain and picking => create a new one
            picking_obj = self.pool.get("stock.picking")
            picking = picking_obj.browse(cr, uid, picking_id, context=context)
            values = {
                'picking_id': picking_id,
                'product_qty': 0,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'qty_done': 1,
            }
            for key in domain:
                var_name, dummy, value = key
                uom_id = False
                if var_name == 'product_id':
                    uom_id = self.pool.get('product.product').browse(cr, uid, value, context=context).uom_id.id
                update_dict = {var_name: value}
                if uom_id:
                    update_dict['product_uom_id'] = uom_id
                values.update(update_dict)
            operation_id = self.create(cr, uid, values, context=context)
        return operation_id

    def create_and_assign_lot(self, cr, uid, id, name, context=None):
        """ Used by barcode interface to create a new lot and assign it to the operation """
        obj = self.browse(cr, uid, id, context)
        product_id = obj.product_id.id
        val = {'product_id': product_id}
        new_lot_id = False
        if name:
            lots = self.pool.get('stock.production.lot').search(
                cr,
                uid,
                ['&', ('name', '=', name), ('product_id', '=', product_id)],
                context=context
            )
            if lots:
                new_lot_id = lots[0]
            val.update({'name': name})

        if not new_lot_id:
            new_lot_id = self.pool.get('stock.production.lot').create(cr, uid, val, context=context)
        self.write(cr, uid, id, {'lot_id': new_lot_id}, context=context)
