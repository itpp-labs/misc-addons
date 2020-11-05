from odoo import models, fields, api, _
from odoo.exceptions import AccessError


class OhadaReportManualEntry(models.Model):
    _name = 'ohada.report.manualentry'
    _description = 'OHADA Report Manual Entry'

    manager_id = fields.Many2one('ohada.report.manager')
    year = fields.Char()
    line = fields.Integer()
    column = fields.Integer()
    type = fields.Selection([('text', 'Test'), ('text', 'Test')])
    text_value = fields.Char()

    @api.multi
    def write(self, vals):
        if not self.env.user.has_group('account.group_account_manager'):
            raise AccessError(_('The requested operation cannot be completed due to security restrictions.'))
        return super(OhadaReportManualEntry, self).write(vals)

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('account.group_account_manager'):
            raise AccessError(_('The requested operation cannot be completed due to security restrictions.'))
        return super(OhadaReportManualEntry, self).create(vals)
