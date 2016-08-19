# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class view(osv.osv):
    _inherit = 'ir.ui.view'

    _columns = {
        'type': fields.selection([
            ('tree', 'Tree'),
            ('form', 'Form'),
            ('graph', 'Graph'),
            ('pivot', 'Pivot'),
            ('calendar', 'Calendar'),
            ('diagram', 'Diagram'),
            ('gantt', 'Gantt'),
            ('gantt8', 'Gantt8'),
            ('kanban', 'Kanban'),
            ('sales_team_dashboard', 'Sales Team Dashboard'),
            ('search', 'Search'),
            ('qweb', 'QWeb')], string='View Type'),
    }
