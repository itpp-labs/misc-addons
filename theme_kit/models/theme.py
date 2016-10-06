# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.base.ir.ir_qweb import AssetsBundle, LessStylesheetAsset


class Theme(models.Model):
    _name = "theme_kit.theme"
    name = fields.Char('Name')
    top_panel_id = fields.Many2one('theme_kit.top_panel', string="Color Schemes for Top Panel")
    left_panel_id = fields.Many2one('theme_kit.left_panel', string="Color Schemes for Left Panel")
    content_id = fields.Many2one('theme_kit.content', string="Color Schemes for Content")
    custom_css = fields.Text(string="Custom CSS/LESS", default=False)
    custom_js = fields.Text(string="Custom JS", default=False)

    code = fields.Text('Code', help='technical computed field', compute='_compute_code')

    @api.multi
    def _compute_code(self):
        for r in self:
            code = ''
            if r.top_panel_id:
                code = code + r.top_panel_id.less
            if r.left_panel_id:
                code = code + r.left_panel_id.less
            if r.content_id:
                code = code + r.content_id.less
            if r.custom_css:
                code = code + r.custom_css
            if code:
                code = self.generate_less2css(code)
            if r.custom_js:
                js_code = r.custom_js
                js_code = 'try {' + js_code + '''
                    } catch (err) {
                      console.log('Error' + err.name + ":" + err.message + ". " + err.stack);
                      alert('Error' + err.name + ":" + err.message + ". " + err.stack);
                    }'''
                code = code + '''<script type="text/javascript" id="custom_js">''' + js_code + '''</script>'''
                r.code = code
            else:
                r.code = code

    def generate_less2css(self, code):
        bundle = AssetsBundle('theme_kit.dummy')
        assets = LessStylesheetAsset(bundle, inline=code, url='')
        cmd = assets.get_command()
        source = assets.get_source()
        compiled = bundle.compile_css(cmd, source)
        compiled = '''<style type="text/css" id="custom_css">''' + compiled + '''</style>'''
        return compiled


class ThemeTopPanel(models.Model):
    _name = "theme_kit.top_panel"

    name = fields.Char('Name')

    top_panel_bg = fields.Char('Background color', help="Menu Bar color for Top Panel")
    top_panel_bg_active = fields.Boolean(default=False, help="Menu Bar color for Top Panel")

    top_panel_border = fields.Char('Border color', help="Border color for Top Panel")
    top_panel_border_active = fields.Boolean(default=False, help="Border color for Top Panel")

    top_panel_font = fields.Char('Font color', help="Font color for Top Panel")
    top_panel_font_active = fields.Boolean(default=False, help="Font color for Top Panel")

    top_panel_active_item_font = fields.Char('Active item Font color', help="Active item Font color for Top Panel")
    top_panel_active_item_font_active = fields.Boolean(default=False, help="Active item Font color for Top Panel")

    top_panel_active_item_bg = fields.Char('Active item Background color', help="Active item Background color for Top Panel")
    top_panel_active_item_bg_active = fields.Boolean(default=False, help="Active item Background color for Top Panel")

    top_panel_hover_item_font = fields.Char('Hover item Font color', help="Hover item Font color for Top Panel")
    top_panel_hover_item_font_active = fields.Boolean(default=False, help="Hover item Font color for Top Panel")

    top_panel_hover_item_bg = fields.Char('Hover item Background color', help="Hover item Background color for Top Panel")
    top_panel_hover_item_bg_active = fields.Boolean(default=False, help="Hover item Background color for Top Panel")

    less = fields.Text('less', help='technical computed field', compute='_compute_less')

    @api.multi
    def _compute_less(self):
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
                }}
                .openerp .oe-control-panel {{
                    border-bottom-color: {theme.top_panel_border}!important;
                }}
                '''
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
            self.less = code


class ThemeLeftPanel(models.Model):
    _name = "theme_kit.left_panel"

    name = fields.Char('Name')

    left_panel_bg = fields.Char('Background color', help="Background Color for Left Menu Bar")
    left_panel_bg_active = fields.Boolean(default=False, help="Background Color for Left Menu Bar")

    left_panel_main_menu = fields.Char('Main Menu Font color', help="Main Menu Font colo for Left Menu Bar")
    left_panel_main_menu_active = fields.Boolean(default=False, help="Main Menu Font colo for Left Menu Bar")

    left_panel_sub_menu = fields.Char('Sub Menu Font color', help="Sub Menu Font colo for Left Menu Bar")
    left_panel_sub_menu_active = fields.Boolean(default=False, help="Sub Menu Font colo for Left Menu Bar")

    left_panel_active_item_font = fields.Char('Active item Font color', help="Active item Font color for Left Menu Bar")
    left_panel_active_item_font_active = fields.Boolean(default=False, help="Active item Font color for Left Menu Bar")

    left_panel_active_item_bg = fields.Char('Active item Background color', help="Active item Background color for Left Menu Bar")
    left_panel_active_item_bg_active = fields.Boolean(default=False, help="Active item Background color for Left Menu Bar")

    left_panel_hover_item_font = fields.Char('Hover item Font color', help="Hover item Font color for Left Menu Bar")
    left_panel_hover_item_font_active = fields.Boolean(default=False, help="Hover item Font color for Left Menu Bar")

    left_panel_hover_item_bg = fields.Char('Hover item Background color', help="Hover item Background color for Left Menu Bar")
    left_panel_hover_item_bg_active = fields.Boolean(default=False, help="Hover item Background color for Left Menu Bar")

    less = fields.Text('less', help='technical computed field', compute='_compute_less')

    @api.multi
    def _compute_less(self):
        for r in self:
            # double {{ will be formated as single {
            code = ''
            if self.left_panel_bg_active:
                code = code + '''.oe_leftbar{{
                    background-color: {theme.left_panel_bg}!important;
                }}
                .o_mail_chat .o_mail_chat_sidebar {{
                    background-color: {theme.left_panel_bg}!important;
                }}
                .o_mail_chat .o_mail_annoying_notification_bar {{
                    background-color: {theme.left_panel_bg}!important;
                }}
                .o_kanban_view.o_kanban_dashboard.o_project_kanban .o_project_kanban_boxes .o_project_kanban_box:nth-child(odd) {{
                    background-color: {theme.left_panel_bg}!important;
                }}
                .o_kanban_view .o_kanban_group:nth-child(odd) {{
                    background-color: {theme.left_panel_bg}!important;
                }}
                .o_kanban_view .o_kanban_group {{
                    .o_column_title{{
                        color: {theme.left_panel_bg}!important;
                    }}

                    .fa-plus, .fa-gear, .fa-arrows-h{{
                        color: {theme.left_panel_bg}!important;
                    }}
                }}
                '''
            if self.left_panel_main_menu_active:
                code = code + '''.oe_leftbar .oe_secondary_menu_section .oe_menu_leaf{{
                    color: {theme.left_panel_main_menu};
                }}
                .oe_leftbar .oe_secondary_menu_section{{
                    color: {theme.left_panel_main_menu};
                }}
                .o_mail_chat .o_mail_chat_sidebar h4{{
                    color: {theme.left_panel_main_menu}!important;
                }}
                .o_kanban_view.o_kanban_dashboard.o_project_kanban .o_project_kanban_boxes .o_value,
                .o_kanban_view.o_kanban_dashboard.o_project_kanban .o_project_kanban_boxes .o_label{{
                    color: {theme.left_panel_main_menu}!important;
                }}
                .o_kanban_view .o_kanban_group:nth-child(odd) {{
                    .o_column_title{{
                        color: {theme.left_panel_main_menu}!important;
                    }}
                    .fa-plus, .fa-gear, .fa-arrows-h{{
                        color: {theme.left_panel_main_menu}!important;
                    }}
                }}
                .o_kanban_view .o_kanban_group {{
                    background-color: {theme.left_panel_main_menu};
                }}
                '''
            if self.left_panel_sub_menu_active:
                code = code + '''.oe_leftbar .oe_secondary_submenu .oe_menu_text{{
                    color: {theme.left_panel_sub_menu};
                }}
                .o_mail_chat .o_mail_chat_sidebar .o_mail_chat_channel_item {{
                    color: {theme.left_panel_sub_menu}!important;
                }}
                .o_mail_request_permission, .o_mail_request_permission a {{
                    color: {theme.left_panel_sub_menu}!important;
                }}
                .o_mail_request_permission a:hover {{
                    color: darken({theme.left_panel_sub_menu}, 10%)!important;
                }}
                '''
            if self.left_panel_active_item_font_active:
                code = code + '''.oe_leftbar .oe_secondary_submenu .active .oe_menu_text{{
                    color: {theme.left_panel_active_item_font}!important;
                }}
                .oe_leftbar .oe_secondary_submenu a:focus .oe_menu_text{{
                    color: {theme.left_panel_active_item_font}!important;
                }}
                .o_mail_chat .o_mail_chat_sidebar .o_mail_chat_channel_item.o_active {{
                    color: {theme.left_panel_active_item_font}!important;
                }}
                '''
            if self.left_panel_active_item_bg_active:
                code = code + '''.oe_leftbar .oe_secondary_submenu .active a{{
                    background-color: {theme.left_panel_active_item_bg}!important;
                }}
                .oe_leftbar .oe_secondary_submenu a:focus{{
                    background-color: {theme.left_panel_active_item_bg}!important;
                }}
                .o_mail_chat .o_mail_chat_sidebar .o_mail_chat_channel_item.o_active {{
                    background-color: {theme.left_panel_active_item_bg}!important;
                }}
                '''
            if self.left_panel_hover_item_font_active:
                code = code + '''.oe_leftbar .oe_secondary_submenu a:hover .oe_menu_text{{
                    color: {theme.left_panel_hover_item_font}!important;
                }}
                .o_mail_chat .o_mail_chat_sidebar .o_mail_chat_channel_item:hover {{
                    color: {theme.left_panel_hover_item_font}!important;
                }}
                '''
            if self.left_panel_hover_item_bg_active:
                code = code + '''.oe_leftbar .oe_secondary_submenu a:hover{{
                    background-color: {theme.left_panel_hover_item_bg}!important;
                }}
                .o_mail_chat .o_mail_chat_sidebar .o_mail_chat_channel_item:hover {{
                    background-color: {theme.left_panel_hover_item_bg}!important;
                }}
                '''
            code = code.format(
                theme=r,
            )
            self.less = code


class ThemeContent(models.Model):
    _name = "theme_kit.content"

    name = fields.Char('Name')

    content_bg = fields.Char('Background color', help="Color for Main page")
    content_bg_active = fields.Boolean(default=False, help="Color for Main page")

    content_button = fields.Char('Button color', help="Button Color for Main page")
    content_button_active = fields.Boolean(default=False, help="Button Color for Main page")

    content_form = fields.Char('Background form color', help="Background form color'")
    content_form_active = fields.Boolean(default=False, help="Background form color'")

    content_form_text = fields.Char('Text form color')
    content_form_text_active = fields.Boolean(default=False, help="Text form color")

    content_form_title = fields.Char('Text title form color')
    content_form_title_active = fields.Boolean(default=False, help="Text title form color")

    content_text = fields.Char('Text content color')
    content_text_active = fields.Boolean(default=False, help="Text content color")

    content_form_link = fields.Char('Link form color')
    content_form_link_active = fields.Boolean(default=False, help="Link form color")

    content_loader = fields.Char('Loader color')
    content_loader_active = fields.Boolean(default=False, help="Loader color")

    content_loader_text = fields.Char('Loader text color')
    content_loader_text_active = fields.Boolean(default=False, help="Loader text color")

    less = fields.Text('less', help='technical computed field', compute='_compute_less')

    @api.multi
    def _compute_less(self):
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
                .openerp .oe_searchview .oe_searchview_facets .oe_searchview_facet .oe_facet_values {{
                    background: lighten({theme.content_bg}, 15%)!important;
                }}
                .openerp .oe-view-manager-view-kanban .oe_background_grey {{
                    background: lighten({theme.content_bg}, 30%) !important;
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
            if self.content_form_link_active:
                code = code + ''' .oe_application a {{
                    color: {theme.content_form_link};
                }}
                '''
            if self.content_button_active:
                code = code + '''.oe_button.oe_highlight,
                .oe_button.btn-primary,
                .btn-primary{{
                    background-color: {theme.content_button} !important;
                    border-color: darken({theme.content_button},10%) !important;
                }}
                oe_button.oe_highlight:hover,
                .oe_button.btn-primary:hover,
                .btn-primary:hover{{
                    background-color: darken({theme.content_button},10%) !important;
                    border-color: darken({theme.content_button},20%) !important;
                }}
                .openerp .oe_tag {{
                    border: 1px solid {theme.content_button} !important;
                }}
                .label-default {{
                    background-color: {theme.content_button} !important;
                }}
                '''
            if self.content_text_active:
                code = code + '''.openerp{{
                    color: {theme.content_text};
                }}
                '''
            if self.content_form_title_active:
                code = code + '''.openerp .oe_horizontal_separator {{
                    color: {theme.content_form_title} !important;
                }}
                .breadcrumb > .active {{
                    color: {theme.content_form_title} !important;
                }}
                .breadcrumb > li + li:before {{
                    color: {theme.content_form_title} !important;
                }}
                '''
            if self.content_loader_active:
                code = code + '''.openerp .oe_loading {{
                    background: {theme.content_loader}!important;
                    border: 1px solid {theme.content_loader}!important;
                    color: darken({theme.content_loader},40%)!important;
                }}'''
            if self.content_loader_text_active:
                code = code + '''.openerp .oe_loading {{
                    color: {theme.content_loader_text}!important;
                }}'''

            code = code.format(
                theme=r,
            )
            self.less = code
