# -*- coding: utf-8 -*-
from openerp import api
from openerp import models
from openerp import models
from openerp.exceptions import AccessError
from openerp.tools.translate import _


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def _attachment_force_storage(self):
        self.env['ir.attachment'].force_storage()

    @api.model
    def create(self, vals):
        res = super(IrConfigParameter, self).create(vals)
        if vals and vals.get('key') == 'ir_attachment.location':
            self._attachment_force_storage()
        return res

    @api.one
    def write(self, vals):
        res = super(IrConfigParameter, self).write(vals)
        if self.key == 'ir_attachment.location':
            self._attachment_force_storage()
        return res


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def force_storage(self):
        """Force all attachments to be stored in the currently configured storage"""
        if not self.env.user._is_admin():
            raise AccessError(_('Only administrators can execute this action.'))

        location = self._storage()
        domain = {
            'db': [('store_fname', '!=', False)],
            'file': [('db_datas', '!=', False)],
        }[location]

        for attach in self.search(domain):
            # we add url because in some environment mimetype is not computed correctly
            attach.write({'datas': attach.datas, 'url': attach.url})
        return True
