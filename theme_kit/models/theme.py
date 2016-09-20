# -*- coding: utf-8 -*-
from openerp import models, fields, api


class Theme(models.Model):
    _name = "theme_kit.theme"

    name = fields.Char('Name')
    main_menu_navbar_bg = fields.Char('Background color', help="Color for Main Menu Bar")
    code = fields.Text('Code', help='technical computed field', compute='_compute_code')

    @api.multi
    def _compute_code(self):
        for r in self:
            # double {{ will be formated as single {
            code = '''
<style type="text/css" id="custom_css">
#oe_main_menu_navbar{{
  background-color: {theme.main_menu_navbar_bg}
}}
</style>
            '''.format(
                theme=r,
            )

            r.code = code
