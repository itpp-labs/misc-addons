# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (c) 2012 OpenERP S.A. <http://openerp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp
from openerp import models, fields, api, SUPERUSER_ID


class ResGroups(models.Model):
    _inherit = 'res.groups'
    
    menu_no_access = fields.Many2many('ir.ui.menu', 'ir_ui_menu_no_group_rel',
                                      'group_id', 'menu_id', 'No Access Menu')


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'
    
    no_groups = fields.Many2many('res.groups', 'ir_ui_menu_no_group_rel',
                                 'menu_id', 'group_id', 'No Groups')
    
    @api.multi
    @api.returns('self')
    def _filter_visible_menus(self):
        menus = super(IrUiMenu, self)._filter_visible_menus()

        if self.env.user.id != SUPERUSER_ID:
            groups = self.env.user.groups_id
            menus = menus.filtered(lambda menu: not(menu.no_groups & groups))
        return menus
