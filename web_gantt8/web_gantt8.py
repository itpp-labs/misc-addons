# -*- coding: utf-8 -*-
# Copyright (c) 2004-2015 Odoo S.A.
# Copyright 2016 Pavel Romanchenko
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0.html).

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
