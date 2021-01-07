# Copyright 2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016,2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models

from odoo.addons.base.models.assetsbundle import AssetsBundle, LessStylesheetAsset


class Theme(models.Model):
    _name = "theme_kit.theme"
    _description = "Theme"
    name = fields.Char("Name", required=True)
    top_panel_id = fields.Many2one(
        "theme_kit.top_panel", string="Color Schemes for Top Panel"
    )
    left_panel_id = fields.Many2one(
        "theme_kit.left_panel", string="Color Schemes for Left Panel"
    )
    content_id = fields.Many2one(
        "theme_kit.content", string="Color Schemes for Content"
    )
    custom_css = fields.Text(string="Custom CSS/LESS", default=False)
    custom_js = fields.Text(string="Custom JS", default=False)

    code = fields.Text("Code", help="technical computed field", compute="_compute_code")

    @api.multi
    def _compute_code(self):
        for r in self:
            code = ""
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
                js_code = (
                    "try {"
                    + js_code
                    + """
                    } catch (err) {
                      console.log('Error' + err.name + ":" + err.message + ". " + err.stack);
                      alert('Error' + err.name + ":" + err.message + ". " + err.stack);
                    }"""
                )
                code = (
                    code
                    + """<script type="text/javascript" id="custom_js">"""
                    + js_code
                    + """</script>"""
                )
            r.code = code

    def generate_less2css(self, code):
        bundle = AssetsBundle("theme_kit.dummy", [], [])
        assets = LessStylesheetAsset(bundle, inline=code, url="")
        source = assets.get_source()
        compiled = bundle.compile_css(assets.compile, source)
        compiled = (
            """<style type="text/css" id="custom_css">""" + compiled + """</style>"""
        )
        return compiled


class ThemeTopPanel(models.Model):
    _name = "theme_kit.top_panel"
    _description = "Settings for Top Panel"

    name = fields.Char("Name", required=True)

    top_panel_bg = fields.Char("Background color", help="Menu Bar color for Top Panel")
    top_panel_bg_active = fields.Boolean(
        default=False, help="Menu Bar color for Top Panel"
    )

    top_panel_border = fields.Char("Border color", help="Border color for Top Panel")
    top_panel_border_active = fields.Boolean(
        default=False, help="Border color for Top Panel"
    )

    top_panel_font = fields.Char("Font color", help="Font color for Top Panel")
    top_panel_font_active = fields.Boolean(
        default=False, help="Font color for Top Panel"
    )

    top_panel_active_item_font = fields.Char(
        "Active item Font color", help="Active item Font color for Top Panel"
    )
    top_panel_active_item_font_active = fields.Boolean(
        default=False, help="Active item Font color for Top Panel"
    )

    top_panel_active_item_bg = fields.Char(
        "Active item Background color",
        help="Active item Background color for Top Panel",
    )
    top_panel_active_item_bg_active = fields.Boolean(
        default=False, help="Active item Background color for Top Panel"
    )

    top_panel_hover_item_font = fields.Char(
        "Hover item Font color", help="Hover item Font color for Top Panel"
    )
    top_panel_hover_item_font_active = fields.Boolean(
        default=False, help="Hover item Font color for Top Panel"
    )

    top_panel_hover_item_bg = fields.Char(
        "Hover item Background color", help="Hover item Background color for Top Panel"
    )
    top_panel_hover_item_bg_active = fields.Boolean(
        default=False, help="Hover item Background color for Top Panel"
    )

    less = fields.Text("less", help="technical computed field", compute="_compute_less")

    @api.multi
    def _compute_less(self):
        for r in self:
            code = ""
            # double {{ will be formated as single {
            if self.top_panel_bg_active:
                code = (
                    code
                    + """
                .o_main_navbar,
                .o_main_navbar .dropdown-menu,
                .o_main_navbar,
                .dropdown-menu,
                .o_calendar_container .o_calendar_view .o_calendar_widget .fc-week-number,
                .o_calendar_container .o_calendar_view .o_calendar_widget .fc-widget-header,
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker .ui-widget-header,
                .datepicker .table-condensed > thead {{
                    background-color: {theme.top_panel_bg};
                }}
                .datepicker .table-condensed > thead th:hover {{
                    background-color: darken({theme.top_panel_bg}, 15%) !important;
                }}
                """
                )

            if self.top_panel_border_active:
                code = (
                    code
                    + """
                .o_main_navbar,
                #oe_main_menu_navbar,
                .o_list_view thead > tr > th {{
                    border-color: {theme.top_panel_border};
                }}
                .o_control_panel {{
                    border-bottom-color: {theme.top_panel_border}!important;
                }}
                .o_form_statusbar .o_arrow_button{{
                    border-color: lighten({theme.top_panel_border}, 40%)!important;
                }}
                .o_form_statusbar .o_arrow_button:before{{
                    border-left-color: lighten({theme.top_panel_border}, 40%)!important;
                }}
                .o_list_view thead {{
                    color: {theme.top_panel_border};
                }}
                """
                )
            if self.top_panel_font_active:
                code = (
                    code
                    + """
                .o_main_navbar .dropdown-item,
                .o_main_navbar .dropdown-toggle,
                .o_main_navbar .o_menu_entry_lvl_1,
                .o_main_navbar .o_menu_brand,
                .o_main_navbar .o_debug_manager a,
                .o_main_navbar .o_menu_apps i,
                .open .dropdown-menu li a span,
                .open .dropdown-menu li.dropdown-header,
                .dropdown-menu li a,
                .o_calendar_container .o_calendar_view .o_calendar_widget .fc-week-number, .o_calendar_container .o_calendar_view .o_calendar_widget .fc-widget-header,
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker .ui-widget-header,
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker .ui-widget-header .ui-datepicker-prev, .o_calendar_container .o_calendar_sidebar_container .ui-datepicker .ui-widget-header .ui-datepicker-next,
                .o_calendar_container .o_calendar_sidebar_container .o_calendar_sidebar_toggler,
                .datepicker .table-condensed > thead {{
                    color: {theme.top_panel_font}!important;
                }}
                .open .dropdown-menu li.dropdown-header {{
                    font-weight: bolder;
                }}
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker .ui-widget-header .ui-datepicker-prev:hover, .o_calendar_container .o_calendar_sidebar_container .ui-datepicker .ui-widget-header .ui-datepicker-next:hover {{
                    color: darken({theme.top_panel_font}, 20%)!important;
                }}
                .o_calendar_container .o_calendar_sidebar_container .o_calendar_sidebar_toggler:hover {{
                    color: darken({theme.top_panel_font}, 20%)!important;
                }}
                """
                )
            if self.top_panel_active_item_font_active:
                code = (
                    code
                    + """
                .navbar-nav .active a,
                .o_main_navbar .dropdown-item.active {{
                    color: {theme.top_panel_active_item_font}!important;
                }}"""
                )
            if self.top_panel_active_item_bg_active:
                code = (
                    code
                    + """
                .navbar-nav .active a,
                .o_main_navbar .dropdown-item.active {{
                    background-color: {theme.top_panel_active_item_bg}!important;
                }}"""
                )
            if self.top_panel_hover_item_font_active:
                code = (
                    code
                    + """
                .o_main_navbar .dropdown-item:hover,
                .o_main_navbar .dropdown-item:focus,
                .navbar-nav li a:hover,
                .navbar-nav li a:focus,
                .o_main_navbar .dropdown-toggle:focus,
                .o_main_navbar .dropdown-toggle:hover,
                .o_main_navbar .o_menu_entry_lvl_1:focus,
                .o_main_navbar .o_menu_entry_lvl_1:hover,
                .open .dropdown-menu > li:hover a span,
                .open .dropdown-menu > li:focus a span,
                .dropdown-menu > li > a:hover,
                .dropdown-menu > li > a:focus,
                .o_main_navbar .o_menu_entry_lvl_1:focus,
                .o_main_navbar .o_menu_entry_lvl_1:hover,
                .o_main_navbar .o_menu_brand:focus,
                .o_main_navbar .o_menu_brand:hover,
                .o_main_navbar .o_debug_manager a:focus,
                .o_main_navbar .o_debug_manager a:hover,
                .o_main_navbar .o_menu_apps:focus i,
                .o_main_navbar .o_menu_apps:hover i
                {{
                    color: {theme.top_panel_hover_item_font}!important;
                }}
                """
                )
            if self.top_panel_hover_item_bg_active:
                code = (
                    code
                    + """
                .o_main_navbar .dropdown-item:hover,
                .o_main_navbar .dropdown-item:focus,
                .navbar-nav li a:hover,
                .navbar-nav li a:focus,
                .o_main_navbar .dropdown-toggle:hover,
                .o_main_navbar .dropdown-toggle:focus,
                .o_main_navbar .o_menu_entry_lvl_1:hover,
                .o_main_navbar .o_menu_entry_lvl_1:focus,
                .open .dropdown-menu li a:hover,
                .open .dropdown-menu li a:focus,
                .o_main_navbar .o_menu_entry_lvl_1:focus,
                .o_main_navbar .o_menu_entry_lvl_1:hover,
                .o_main_navbar .o_menu_brand:focus,
                .o_main_navbar .o_menu_brand:hover,
                .o_main_navbar .o_debug_manager a:focus,
                .o_main_navbar .o_debug_manager a:hover,
                .o_main_navbar .o_menu_apps:focus .full,
                .o_main_navbar .o_menu_apps:hover .full {{
                    background-color: {theme.top_panel_hover_item_bg}!important;
                }}
                """
                )
            code = code.format(theme=r)
            self.less = code


class ThemeLeftPanel(models.Model):
    _name = "theme_kit.left_panel"
    _description = "Settings for Left Panel"

    name = fields.Char("Name", required=True)

    left_panel_bg = fields.Char("Background color", help="Background Color")
    left_panel_bg_active = fields.Boolean(default=False, help="Background Color")

    left_panel_font_color = fields.Char("Font color", help="Font color")
    left_panel_font_color_active = fields.Boolean(default=False, help="Font color")

    left_panel_menu = fields.Char(
        "Menu Font color", help="Menu Font color for Left Menu Bar"
    )
    left_panel_menu_active = fields.Boolean(
        default=False, help="Menu Font color for Left Menu Bar"
    )

    left_panel_active_item_font = fields.Char(
        "Active item Font color", help="Active item Font color for Left Menu Bar"
    )
    left_panel_active_item_font_active = fields.Boolean(
        default=False, help="Active item Font color for Left Menu Bar"
    )

    left_panel_active_item_bg = fields.Char(
        "Active item Background color",
        help="Active item Background color for Left Menu Bar",
    )
    left_panel_active_item_bg_active = fields.Boolean(
        default=False, help="Active item Background color for Left Menu Bar"
    )

    left_panel_hover_item_font = fields.Char(
        "Hover item Font color", help="Hover item Font color for Left Menu Bar"
    )
    left_panel_hover_item_font_active = fields.Boolean(
        default=False, help="Hover item Font color for Left Menu Bar"
    )

    left_panel_hover_item_bg = fields.Char(
        "Hover item Background color",
        help="Hover item Background color for Left Menu Bar",
    )
    left_panel_hover_item_bg_active = fields.Boolean(
        default=False, help="Hover item Background color for Left Menu Bar"
    )

    less = fields.Text("less", help="technical computed field", compute="_compute_less")

    @api.multi
    def _compute_less(self):
        for r in self:
            # double {{ will be formated as single {
            code = ""
            if self.left_panel_bg_active:
                code = (
                    code
                    + """
                .o_mail_discuss .o_mail_discuss_sidebar,
                .o_base_settings .o_setting_container .settings_tab {{
                    background-color: {theme.left_panel_bg}!important;
                    background: {theme.left_panel_bg}!important;
                }}
                """
                )
            if self.left_panel_font_color_active:
                code = (
                    code
                    + """
                .o_base_settings .o_setting_container .settings_tab .selected .app_name,
                .o_mail_discuss .o_mail_discuss_sidebar .o_mail_discuss_item .o_thread_name {{
                    color: {theme.left_panel_font_color}!important;
                }}
                """
                )
            if self.left_panel_menu_active:
                code = (
                    code
                    + """
                .o_mail_sidebar_title h4 {{
                    color: {theme.left_panel_menu}!important;
                }}
                """
                )
            if self.left_panel_active_item_font_active:
                code = (
                    code
                    + """
                .o_base_settings .o_setting_container .settings_tab .selected .app_name,
                .o_mail_discuss .o_mail_discuss_sidebar .o_mail_discuss_item.o_active .o_thread_name {{
                    color: {theme.left_panel_active_item_font}!important;
                }}
                """
                )
            if self.left_panel_active_item_bg_active:
                code = (
                    code
                    + """
                .o_mail_discuss .o_mail_discuss_sidebar .o_mail_discuss_item.o_active,
                .o_base_settings .o_setting_container .settings_tab .selected {{
                    background-color: {theme.left_panel_active_item_bg}!important;
                }}
                """
                )
            if self.left_panel_hover_item_font_active:
                code = (
                    code
                    + """
                .o_base_settings .o_setting_container .settings_tab .tab:hover .app_name,
                .o_mail_discuss .o_mail_discuss_sidebar .o_mail_discuss_item.o_mail_discuss_title_main:hover .o_thread_name,
                .o_mail_discuss .o_mail_discuss_sidebar .o_mail_discuss_item:hover .o_thread_name {{
                    color: {theme.left_panel_hover_item_font}!important;
                }}
                """
                )
            if self.left_panel_hover_item_bg_active:
                code = (
                    code
                    + """
                .o_base_settings .o_setting_container .settings_tab .tab:hover,
                .o_mail_discuss .o_mail_discuss_sidebar .o_mail_discuss_item.o_mail_discuss_title_main:hover{{
                    background-color: {theme.left_panel_hover_item_bg}!important;
                }}
                """
                )

            code = code.format(
                theme=r,
            )
            self.less = code


class ThemeContent(models.Model):
    _name = "theme_kit.content"
    _description = "Settings for Content"

    name = fields.Char("Name", required=True)

    content_bg = fields.Char("Background color", help="Color for Main page")
    content_bg_active = fields.Boolean(default=False, help="Color for Main page")

    content_button = fields.Char("Button color", help="Button Color for Main page")
    content_button_active = fields.Boolean(
        default=False, help="Button Color for Main page"
    )

    content_form = fields.Char("Background form color", help="Background form color")
    content_form_active = fields.Boolean(default=False, help="Background form color")

    content_form_text = fields.Char("Text form color")
    content_form_text_active = fields.Boolean(default=False, help="Text form color")

    content_form_title = fields.Char("Text title form color")
    content_form_title_active = fields.Boolean(
        default=False, help="Text title form color"
    )

    content_text = fields.Char("Text content color")
    content_text_active = fields.Boolean(default=False, help="Text content color")

    content_form_link = fields.Char("Link form color")
    content_form_link_active = fields.Boolean(default=False, help="Link form color")

    content_loader = fields.Char("Loader color")
    content_loader_active = fields.Boolean(default=False, help="Loader color")

    content_loader_text = fields.Char("Loader text color")
    content_loader_text_active = fields.Boolean(default=False, help="Loader text color")

    content_statusbar_bg = fields.Char(
        "Status Bar Background color", help="Status Bar Background color"
    )
    content_statusbar_bg_active = fields.Boolean(
        default=False, help="Status Bar Background color"
    )

    content_statusbar_element = fields.Char(
        "Status Bar Current State color", help="Status Bar Current State color"
    )
    content_statusbar_element_active = fields.Boolean(
        default=False, help="Status Bar Current State Background color"
    )

    content_statusbar_font_color = fields.Char(
        "Status Bar Font color", help="Status Bar Font color"
    )
    content_statusbar_font_color_active = fields.Boolean(
        default=False, help="Status Bar Font color"
    )

    content_main_menu_font_color = fields.Char(
        "Main menu font color", help="Main menu font color"
    )
    content_main_menu_font_color_active = fields.Boolean(
        default=False, help="Main menu font color"
    )

    content_footer_color = fields.Char("Footer color", help="Footer color")
    content_footer_color_active = fields.Boolean(default=False, help="Footer color")
    less = fields.Text("less", help="technical computed field", compute="_compute_less")

    @api.multi
    def _compute_less(self):
        for r in self:
            code = ""
            if self.content_bg_active:
                code = (
                    code
                    + """
                .breadcrumb,
                .o_control_panel,
                .o_statusbar_buttons,
                .o_content {{
                    background-color: {theme.content_bg}!important;
                }}
                .o_form_view header{{
                    border-bottom: 1px solid darken({theme.content_bg}, 10%) !important;
                    background-color: lighten({theme.content_bg}, 30%) !important;
                    background-image: linear-gradient(to bottom, lighten({theme.content_bg}, 30%), {theme.content_bg}) !important;
                    background-image: -webkit-gradient(linear, left top, left bottom, from(lighten({theme.content_bg}, 30%)), to({theme.content_bg})) !important;
                    background-image: -webkit-linear-gradient(top, lighten({theme.content_bg}, 30%), {theme.content_bg}) !important;
                    background-image: -moz-linear-gradient(top, lighten({theme.content_bg}, 30%), {theme.content_bg}) !important;
                    background-image: -ms-linear-gradient(top, lighten({theme.content_bg}, 30%), {theme.content_bg})!important;
                    background-image: -o-linear-gradient(top, lighten({theme.content_bg}, 30%), {theme.content_bg})!important;
                }}
                .o_list_view thead {{
                    background: lighten({theme.content_bg}, 15%)!important;
                    border-bottom: 2px solid darken({theme.content_bg}, 10%)!important;
                }}
                .o_list_view tfoot {{
                    border-top: 2px solid darken({theme.content_bg}, 10%)!important;
                    border-bottom: 1px solid darken({theme.content_bg}, 10%)!important;
                    background: lighten({theme.content_bg}, 15%)!important;
                }}
                .table-striped > tbody > tr:nth-of-type(odd) {{
                    background-color: lighten({theme.content_bg}, 15%)!important;
                    background-image: -webkit-gradient(linear, left top, left bottom, from(lighten({theme.content_bg}, 20%)), to(lighten({theme.content_bg}, 15%)))!important;
                    background-image: -webkit-linear-gradient(top,lighten({theme.content_bg}, 20%), lighten({theme.content_bg}, 15%));
                    background-image: -moz-linear-gradient(top, lighten({theme.content_bg}, 20%), lighten({theme.content_bg}, 15%));
                    background-image: -ms-linear-gradient(top, lighten({theme.content_bg}, 20%), lighten({theme.content_bg}, 15%));
                    background-image: -o-linear-gradient(top, lighten({theme.content_bg}, 20%), lighten({theme.content_bg}, 15%));
                    background-image: linear-gradient(to bottom, lighten({theme.content_bg}, 20%), lighten({theme.content_bg}, 15%));
                }}
                .o_list_view tbody tr {{
                    border-top: 1px solid darken({theme.content_bg}, 10%)!important;
                }}
                .o_web_settings_dashboard {{
                    background: lighten({theme.content_bg}, 20%)!important;
                }}
                .o_main .o_form_sheet_bg,
                .o_content .o_form_sheet_bg {{
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
                .o_facet_values {{
                    background: lighten({theme.content_bg}, 15%)!important;
                }}
                .o_main .o-view-manager-view-kanban .o_background_grey {{
                    background: lighten({theme.content_bg}, 30%) !important;
                }}
                .o_application_switcher {{
                    background-image: none;
                    background-color: {theme.content_bg};
                    background: -moz-linear-gradient(135deg, lighten({theme.content_bg}, 30%), {theme.content_bg});
                    background: -o-linear-gradient(135deg, lighten({theme.content_bg}, 30%), {theme.content_bg});
                    background: -webkit-gradient(linear, left top, right bottom, from(lighten({theme.content_bg}, 30%)), to({theme.content_bg}));
                    background: -ms-linear-gradient(top, lighten({theme.content_bg}, 30%), {theme.content_bg});
                }}
                .o_application_switcher .o_app:hover{{
                    background-color: darken({theme.content_bg}, 1%) !important;
                }}
                """
                )

            if self.content_form_active:
                code = (
                    code
                    + """
                .o_form,
                .table-responsive,
                .o-x2m-control-panel {{
                    background-color: {theme.content_form}
                }}
                .o_form_sheet {{
                    background: {theme.content_form}!important
                }}
                .o_list_content tbody tr:nth-child(even) {{
                    background-color: {theme.content_form} !important;
                    background-image: -webkit-gradient(linear, left top, left bottom, from(lighten({theme.content_form}, 5%)), to({theme.content_form}))!important;
                    background-image: -webkit-linear-gradient(top,lighten({theme.content_form}, 5%), {theme.content_form});
                    background-image: -moz-linear-gradient(top, lighten({theme.content_form}, 5%), {theme.content_form});
                    background-image: -ms-linear-gradient(top, lighten({theme.content_form}, 5%), {theme.content_form});
                    background-image: -o-linear-gradient(top, lighten({theme.content_form}, 5%), {theme.content_form});
                    background-image: linear-gradient(to bottom, lighten({theme.content_form}, 5%), {theme.content_form});
                }}
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker table td a {{
                    background-color: darken({theme.content_form}, 10%);
                }}
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker table td,
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker table thead,
                .datepicker .table-condensed,
                .datepicker .table-condensed > thead > tr:last-child {{
                    background-color: {theme.content_form};
                }}
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker table .ui-state-active,
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker table td a:hover {{
                    background-color: darken({theme.content_form}, 25%);
                }}
                .datepicker .table-condensed > thead > tr:last-child th:hover,
                .datepicker .table-condensed > tbody > tr > td.active, .datepicker .table-condensed > tbody > tr > td .active {{
                    background-color: darken({theme.content_form}, 15%);
                }}
                .bootstrap-datetimepicker-widget td.day:hover, .bootstrap-datetimepicker-widget td.hour:hover, .bootstrap-datetimepicker-widget td.minute:hover, .bootstrap-datetimepicker-widget td.second:hover {{
                    background-color: lighten({theme.content_form}, 15%);
                }}
                """
                )
            if self.content_form_text_active:
                code = (
                    code
                    + """
                .o_form_view,
                .o_form,
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker table .ui-state-default,
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker table thead,
                .datepicker .table-condensed > thead > tr:last-child,
                .datepicker .table-condensed {{
                    color: {theme.content_form_text};
                }}
                .o_horizontal_separator {{
                    color: darken({theme.content_form_text}, 20%) !important;
                }}
                .nav-tabs li .active a {{
                    color: {theme.content_form_text} !important;
                }}
                .o_form div.o_form_configuration p, .o_main .o_form div.o_form_configuration ul, .o_main .o_form div.o_form_configuration ol {{
                    color: darken({theme.content_form_text}, 10%) !important;
                }}
                .o_calendar_container .o_calendar_sidebar_container .ui-datepicker table .ui-state-active {{
                    color: lighten({theme.content_form_text}, 30%)!important;
                }}
                """
                )
            if self.content_form_link_active:
                code = (
                    code
                    + """
                .o_main_content a,
                .o_control_panel .breadcrumb > li > a,
                .o_control_panel .dropdown-toggle,
                .o_control_panel .o_cp_right,
                .o_control_panel .o_pager_previous,
                .o_control_panel .o_pager_next {{
                    color: {theme.content_form_link};
                }}
                """
                )
            if self.content_button_active:
                code = (
                    code
                    + """.oe_highlight,
                .o_button.btn-primary,
                .btn-primary{{
                    background-color: {theme.content_button} !important;
                    border-color: darken({theme.content_button},10%) !important;
                }}
                o_button.o_highlight:hover,
                .o_button.btn-primary:hover,
                .btn-primary:hover{{
                    background-color: darken({theme.content_button},10%) !important;
                    border-color: darken({theme.content_button},20%) !important;
                }}
                .o_statusbar_status > .o_arrow_button.btn-primary.disabled:after {{
                    border-left-color: {theme.content_button}!important;
                }}
                .o_main .e_tag {{
                    border: 1px solid {theme.content_button} !important;
                }}
                .o_searchview_facet_label {{
                    background-color: {theme.content_button} !important;
                }}
                .o_searchview .o_searchview_facet .o_facet_remove {{
                    color: {theme.content_button} !important;
                }}
                """
                )
            if self.content_text_active:
                code = (
                    code
                    + """.o_main{{
                    color: {theme.content_text} !important;
                }}
                """
                )
            if self.content_form_title_active:
                code = (
                    code
                    + """
                .o_horizontal_separator,
                .o_main .o_horizontal_separator,
                .o_form_label,
                .breadcrumb > .active,
                .breadcrumb > li + li:before {{
                    color: {theme.content_form_title} !important;
                }}
                """
                )
            if self.content_loader_active:
                code = (
                    code
                    + """.o_loading {{
                    background: {theme.content_loader}!important;
                    border: 1px solid {theme.content_loader}!important;
                    color: darken({theme.content_loader},40%)!important;
                }}"""
                )
            if self.content_loader_text_active:
                code = (
                    code
                    + """.o_loading {{
                    color: {theme.content_loader_text}!important;
                }}"""
                )
            if self.content_statusbar_bg_active:
                code = (
                    code
                    + """.o_form_statusbar,
                .o_form_statusbar .btn-default {{
                    background-color: {theme.content_statusbar_bg}!important;
                }}
                .o_form_view .o_form_statusbar > .o_statusbar_status > .o_arrow_button:before,
                .o_form_view .o_form_statusbar > .o_statusbar_status > .o_arrow_button:after
                {{
                    border-left-color: {theme.content_statusbar_bg};
                }}
                """
                )
            if self.content_statusbar_element_active:
                code = (
                    code
                    + """.o_form_view .o_form_statusbar > .o_statusbar_status > .o_arrow_button.btn-primary.disabled,
                .o_form_view .o_form_statusbar > .o_statusbar_status > .o_arrow_button.btn-primary.disabled .o_arrow_button:after,
                .o_form_statusbar .btn-default:hover, .o_form_statusbar .btn-default:focus {{
                    background-color: {theme.content_statusbar_element}!important;
                }}
                .o_statusbar_status > .o_arrow_button.btn-primary.disabled:after,
                .o_form_view .o_form_statusbar > .o_statusbar_status > .o_arrow_button:not(.disabled):hover:after,
                .o_statusbar_status > .o_arrow_button:not(.disabled):focus:after {{
                    border-left-color: {theme.content_statusbar_element}!important;
                }}
                """
                )
            if self.content_statusbar_font_color_active:
                code = (
                    code
                    + """.o_form_view .o_form_statusbar .o_statusbar_status .o_arrow_button {{
                    color: lighten({theme.content_statusbar_font_color}, 25%)
                }}
                .o_form_view .o_form_statusbar .o_statusbar_status .o_arrow_button.btn-primary.disabled {{
                    color: {theme.content_statusbar_font_color}
                }}
                .o_form_view .o_form_statusbar .o_statusbar_status .dropdown-menu .o_arrow_button {{
                    color: lighten({theme.content_statusbar_font_color}, 25%) !important
                }}
                .o_form_view .o_form_statusbar .o_statusbar_status .dropdown-menu .o_arrow_button {{
                    color: {theme.content_statusbar_font_color}!important
                }}
                """
                )
            if self.content_main_menu_font_color_active:
                code = (
                    code
                    + """.o_application_switcher .o_caption {{
                    color: {theme.content_main_menu_font_color}!important
                }}
                """
                )
            if self.content_footer_color_active:
                code = (
                    code
                    + """.o_view_manager_content {{
                    background-color: {theme.content_footer_color}!important
                }}
                """
                )

            code = code.format(theme=r)
            self.less = code
