# -*- coding: utf-8 -*-
from openerp.osv import osv,fields

class res_users(osv.Model):
    _inherit = 'res.users'

    _columns = {
    }

    def action_clear_access_rights(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        user = self.browse(cr, uid, ids[0], context=context)
        admin_groups = [
            self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_user')[1],
            self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_erp_manager')[1],
            self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_system')[1]
        ]
            

        groups_id = []
        for g in user.groups_id:
            if uid==user.id and g.id in admin_groups:
                # don't allow to admin to clear his rights
                continue
            groups_id.append((3,g.id))
        user.write({'groups_id':groups_id})
        return True
