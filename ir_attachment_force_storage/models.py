# -*- coding: utf-8 -*-
from openerp import api
from openerp import models
from openerp.exceptions import AccessError
from openerp.tools.translate import _

STORAGE_KEY = 'ir_attachment.location'


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def _attachment_force_storage(self, previous_value):
        self.env['ir.attachment'].force_storage_previous(previous_value=previous_value)

    @api.model
    def create(self, vals):
        res = super(IrConfigParameter, self).create(vals)
        if vals and vals.get('key') == STORAGE_KEY:
            default_value = self.env['ir.attachment']._storage()
            self._attachment_force_storage(default_value)
        return res

    @api.multi
    def _get_storage_value(self):
        for r in self:
            if self.key == STORAGE_KEY:
                return r.value
        return None

    @api.multi
    def write(self, vals):
        storage_value = self._get_storage_value()
        res = super(IrConfigParameter, self).write(vals)
        if storage_value:
            self._attachment_force_storage(storage_value)
        return res

    @api.multi
    def unlink(self):
        storage_value = self._get_storage_value()
        res = super(IrConfigParameter, self).unlink()
        if storage_value:
            self._attachment_force_storage(storage_value)
        return res


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    def force_storage_previous(self, cr, uid, previous_value=None, context=None):
        """Force all attachments to be stored in the currently configured storage"""
        if not self.pool['res.users'].has_group(cr, uid, 'base.group_erp_manager'):
            raise AccessError(_('Only administrators can execute this action.'))
        new_value = self._storage(cr, uid)
        if all([v in ['db', 'file'] for v in [new_value, previous_value]]):
            # Switching between file and db.
            # We can reduce records to be updated.
            domain = {
                'db': [('store_fname', '!=', False)],
                'file': [('db_datas', '!=', False)],
            }.get(new_value, [])
        else:
            # Update all records if it's not standart switching
            domain = []

        ids = self.search(cr, uid, domain, context=context)
        for attach in self.browse(cr, uid, ids, context=context):
            attach.write({'datas': attach.datas})
        return True
