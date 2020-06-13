from odoo import models, fields, api, _


class OhadaReportManualEntry(models.Model):
    _name = 'ohada.report.manualentry'
    _description = 'OHADA Report Manual Entry'

    manager_id = fields.Many2one('ohada.report.manager')
    year = fields.Char()
    line = fields.Integer()
    column = fields.Integer()
    type = fields.Selection([('text', 'Test'), ('text', 'Test')])
    text_value = fields.Char()
