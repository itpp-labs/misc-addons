# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.base.ir.ir_qweb import AssetsBundle, LessStylesheetAsset


class Theme(models.Model):
    _name = "theme_kit.theme"
    name = fields.Char('Name')
    top_panel_id = fields.Many2one('theme_kit.top_panel', string="Color Schemes for Top Panel")
    left_panel_id = fields.Many2one('theme_kit.left_panel', string="Color Schemes for Left Panel")
    content_id = fields.Many2one('theme_kit.content', string="Color Schemes for Content")

    code = fields.Text('Code', help='technical computed field', compute='_compute_code')

    @api.multi
    def _compute_code(self):
        for r in self:
            code = ''
            if r.top_panel_id:
                code = code + r.top_panel_id.code
            if r.left_panel_id:
                code = code + r.left_panel_id.code
            if r.content_id:
                code = code + r.content_id.code
            bundle = AssetsBundle('theme_kit.dummy')
            assets = LessStylesheetAsset(bundle, inline=code, url='')
            cmd = assets.get_command()
            source = assets.get_source()
            # source = '\n'.join([asset.get_source() for asset in assets])
            compiled = bundle.compile_css(cmd, source)
            compiled = '''<style type="text/css" id="theme_kit.custom_css">''' + compiled + '''</style>'''
            r.code = compiled


class ThemeTopPanel(models.Model):
    _name = "theme_kit.top_panel"

    name = fields.Char('Name')

    top_panel_bg = fields.Char('Background color', help="Menu Bar color for Top Panel")
    top_panel_bg_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    top_panel_border = fields.Char('Border color', help="Border color for Top Panel")
    top_panel_border_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    top_panel_font = fields.Char('Font color', help="Font color for Top Panel")
    top_panel_font_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    top_panel_active_item_font = fields.Char('Active item Font color', help="Active item Font color for Top Panel")
    top_panel_active_item_font_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    top_panel_active_item_bg = fields.Char('Active item Background color', help="Active item Background color for Top Panel")
    top_panel_active_item_bg_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    top_panel_hover_item_font = fields.Char('Hover item Font color', help="Hover item Font color for Top Panel")
    top_panel_hover_item_font_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    top_panel_hover_item_bg = fields.Char('Hover item Background color', help="Hover item Background color for Top Panel")
    top_panel_hover_item_bg_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    code = fields.Text('Code', help='technical computed field', compute='_compute_code')

    @api.multi
    def _compute_code(self):
        for r in self:
            code = ''
            # double {{ will be formated as single {
            if self.top_panel_bg_active:
                code = code + '''
                #oe_main_menu_navbar{{
                background-color: {theme.top_panel_bg};
                }}
                #oe_main_menu_navbar .dropdown-menu{{
                background-color: {theme.top_panel_bg};
                }}'''

            if self.top_panel_border_active:
                code = code + '''#oe_main_menu_navbar{{
                border-color: {theme.top_panel_border};
                }}'''
            if self.top_panel_font_active:
                code = code + '''.navbar-nav li a{{
                color: {theme.top_panel_font}!important;
                }}'''
            if self.top_panel_active_item_font_active:
                code = code + '''.navbar-nav .active a{{
                color: {theme.top_panel_active_item_font}!important;
                }}'''
            if self.top_panel_active_item_bg_active:
                code = code + '''.navbar-nav .active a{{
                background-color: {theme.top_panel_active_item_bg}!important;
                }}'''
            if self.top_panel_hover_item_font_active:
                code = code + '''.navbar-nav li a:hover{{
                color: {theme.top_panel_hover_item_font}!important;
                }}
                .navbar-nav li a:focus{{
                color: {theme.top_panel_hover_item_font}!important;
                }}'''
            if self.top_panel_hover_item_bg_active:
                code = code + '''.navbar-nav li a:hover{{
                background-color: {theme.top_panel_hover_item_bg}!important;
                }}
                .navbar-nav li a:focus{{
                background-color: {theme.top_panel_hover_item_bg}!important;
                }}'''
            code = code.format(
                theme=r,
            )
            self.code = code



class ThemeLeftPanel(models.Model):
    _name = "theme_kit.left_panel"

    name = fields.Char('Name')

    left_panel_bg = fields.Char('Background color', help="Background Color for Left Menu Bar")
    left_panel_bg_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    left_panel_main_menu = fields.Char('Main Menu Font color', help="Main Menu Font colo for Left Menu Bar")
    left_panel_main_menu_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    left_panel_sub_menu = fields.Char('Sub Menu Font color', help="Sub Menu Font colo for Left Menu Bar")
    left_panel_sub_menu_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    left_panel_active_item_font = fields.Char('Active item Font color', help="Active item Font color for Left Menu Bar")
    left_panel_active_item_font_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    left_panel_active_item_bg = fields.Char('Active item Background color', help="Active item Background color for Left Menu Bar")
    left_panel_active_item_bg_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    left_panel_hover_item_font = fields.Char('Hover item Font color', help="Hover item Font color for Left Menu Bar")
    left_panel_hover_item_font_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    left_panel_hover_item_bg = fields.Char('Hover item Background color', help="Hover item Background color for Left Menu Bar")
    left_panel_hover_item_bg_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    code = fields.Text('Code', help='technical computed field', compute='_compute_code')

    @api.multi
    def _compute_code(self):
        for r in self:
            # double {{ will be formated as single {
            code = ''
            if self.left_panel_bg_active:
                code = code + '''.oe_leftbar{{
                background-color: {theme.left_panel_bg}!important;
                }}'''
            if self.left_panel_main_menu_active:
                code = code + '''.oe_leftbar .oe_secondary_menu_section .oe_menu_leaf{{
                color: {theme.left_panel_main_menu};
                }}
                .oe_leftbar .oe_secondary_menu_section{{
                color: {theme.left_panel_main_menu};
                }}'''
            if self.left_panel_sub_menu_active:
                code = code + '''.oe_leftbar .oe_secondary_submenu .oe_menu_text{{
                color: {theme.left_panel_sub_menu};
                }}'''
            if self.left_panel_active_item_font_active:
                code = code + '''.oe_leftbar .oe_secondary_submenu .active .oe_menu_text{{
                color: {theme.left_panel_active_item_font}!important;
                }}
                .oe_leftbar .oe_secondary_submenu a:focus .oe_menu_text{{
                color: {theme.left_panel_active_item_font}!important;
                }}'''
            if self.left_panel_active_item_bg_active:
                code = code + '''.oe_leftbar .oe_secondary_submenu .active a{{
                background-color: {theme.left_panel_active_item_bg}!important;
                }}
                .oe_leftbar .oe_secondary_submenu a:focus{{
                background-color: {theme.left_panel_active_item_bg}!important;
                }}'''
            if self.left_panel_hover_item_font_active:
                code = code + '''.oe_leftbar .oe_secondary_submenu a:hover .oe_menu_text{{
                color: {theme.left_panel_hover_item_font}!important;
                }}'''
            if self.left_panel_hover_item_bg_active:
                code = code + '''.oe_leftbar .oe_secondary_submenu a:hover{{
                background-color: {theme.left_panel_hover_item_bg}!important;
                }}'''
            code = code.format(
                theme=r,
            )
            self.code = code


class ThemeContent(models.Model):
    _name = "theme_kit.content"

    name = fields.Char('Name')

    content_bg = fields.Char('Background color', help="Color for Main page")
    content_bg_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    content_button = fields.Char('Button color', help="Button Color for Main page")
    content_button_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    content_form = fields.Char('Background form color')
    content_form_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    content_form_text = fields.Char('Text form color')
    content_form_text_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    content_form_link = fields.Char('Link form color')
    content_form_link_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    code = fields.Text('Code', help='technical computed field', compute='_compute_code')

    @api.multi
    def _compute_code(self):
        for r in self:
            code = ''
            if self.content_bg_active:
                code = code + '''.oe_application .oe-control-panel,
                .oe_application .oe-control-panel .oe-view-title{{
                    background-color: {theme.content_bg}!important;
                }}
                .oe_form header{{
                    border-bottom: 1px solid darken({theme.content_bg}, 10%) !important;
                    background-color: lighten({theme.content_bg}, 30%) !important;
                    background-image: linear-gradient(to bottom, lighten({theme.content_bg}, 30%), {theme.content_bg}) !important;
                    background-image: -webkit-gradient(linear, left top, left bottom, from(lighten({theme.content_bg}, 30%)), to({theme.content_bg})) !important;
                    background-image: -webkit-linear-gradient(top, lighten({theme.content_bg}, 30%), {theme.content_bg}) !important;
                    background-image: -moz-linear-gradient(top, lighten({theme.content_bg}, 30%), {theme.content_bg}) !important;
                    background-image: -ms-linear-gradient(top, lighten({theme.content_bg}, 30%), {theme.content_bg})!important;
                    background-image: -o-linear-gradient(top, lighten({theme.content_bg}, 30%), {theme.content_bg})!important;
                }}
                .oe-view-manager {{
                    background-color: {theme.content_bg}!important;
                }}
                .oe_list_content thead {{
                    background: lighten({theme.content_bg}, 15%)!important;
                    border-bottom: 2px solid darken({theme.content_bg}, 10%)!important;
                }}
                .oe_list_content tfoot {{
                    border-top: 2px solid darken({theme.content_bg}, 10%)!important;
                    border-bottom: 1px solid darken({theme.content_bg}, 10%)!important;
                    background: lighten({theme.content_bg}, 15%)!important;
                }}
                .oe_list_content tbody tr:nth-child(odd) {{
                    background-color: lighten({theme.content_bg}, 15%)!important;
                    background-image: -webkit-gradient(linear, left top, left bottom, from(lighten({theme.content_bg}, 20%)), to(lighten({theme.content_bg}, 15%)))!important;
                    background-image: -webkit-linear-gradient(top,lighten({theme.content_bg}, 20%), lighten({theme.content_bg}, 15%));
                    background-image: -moz-linear-gradient(top, lighten({theme.content_bg}, 20%), lighten({theme.content_bg}, 15%));
                    background-image: -ms-linear-gradient(top, lighten({theme.content_bg}, 20%), lighten({theme.content_bg}, 15%));
                    background-image: -o-linear-gradient(top, lighten({theme.content_bg}, 20%), lighten({theme.content_bg}, 15%));
                    background-image: linear-gradient(to bottom, lighten({theme.content_bg}, 20%), lighten({theme.content_bg}, 15%));
                }}
                .oe_list_content tbody tr {{
                    border-top: 1px solid darken({theme.content_bg}, 10%)!important;
                }}
                .o_web_settings_dashboard {{
                    background: lighten({theme.content_bg}, 20%)!important;
                }}
                .oe_application .oe_form_sheetbg {{
                    background: lighten({theme.content_bg}, 30%)!important;
                }}
                .nav-tabs {{
                    border-bottom: 1px solid lighten({theme.content_bg}, 15%)!important;
                }}
                .nav-tabs > li.active > a, .nav-tabs > li.active > a:hover, .nav-tabs > li.active > a:focus {{
                    background-color: lighten({theme.content_bg}, 15%)!important;
                    border: 1px solid lighten({theme.content_bg}, 15%)!important;
                }}
                .o_kanban_view {{
                    background-color: lighten({theme.content_bg}, 30%) !important;
                }}
                '''

            if self.content_form_active:
                code = code + '''.oe_form{{
                    background-color: {theme.content_form}
                }}
                .oe_form_sheet {{
                    background: {theme.content_form}!important
                }}
                .oe-x2m-control-panel {{
                    background-color: {theme.content_form}!important;
                }}
                .oe_list_content tbody tr:nth-child(even) {{
                    background-color: {theme.content_form} !important;
                    background-image: -webkit-gradient(linear, left top, left bottom, from(lighten({theme.content_form}, 5%)), to({theme.content_form}))!important;
                    background-image: -webkit-linear-gradient(top,lighten({theme.content_form}, 5%), {theme.content_form});
                    background-image: -moz-linear-gradient(top, lighten({theme.content_form}, 5%), {theme.content_form});
                    background-image: -ms-linear-gradient(top, lighten({theme.content_form}, 5%), {theme.content_form});
                    background-image: -o-linear-gradient(top, lighten({theme.content_form}, 5%), {theme.content_form});
                    background-image: linear-gradient(to bottom, lighten({theme.content_form}, 5%), {theme.content_form});
                }}
                '''
            if self.content_form_text_active:
                code = code + '''.oe_form {{
                    color: {theme.content_form_text} !important;
                }}
                .oe_horizontal_separator {{
                    color: darken({theme.content_form_text}, 20%) !important;
                }}
                .nav-tabs li .active a {{
                    color: {theme.content_form_text} !important;
                }}
                .oe_form div.oe_form_configuration p, .openerp .oe_form div.oe_form_configuration ul, .openerp .oe_form div.oe_form_configuration ol {{
                    color: darken({theme.content_form_text}, 10%) !important;
                }}
                '''
                # if self.content_button_active:

            code = code.format(
                theme=r,
            )
            self.code = code
