
import hashlib

from openerp import models, fields, api

CUSTOM_CSS_ARCH = '''<?xml version="1.0"?>
<t t-name="theme_kit.custom_css">
%s
</t>
'''


class Config(models.TransientModel):

    _name = 'theme_kit.config'
    _inherit = 'res.config.settings'

    theme_id = fields.Many2one('theme_kit.theme', string="Color Scheme")
    favicon_id = fields.Many2one('ir.attachment', string="Favicon")

    page_title = fields.Char('Page Title', help='''Anything you want to see in page title, e.g.
* CompanyName
* CompanyName's Portal
* CompanyName's Operation System
* etc.
    ''')
    system_name = fields.Char('System Name', help='''e.g.
* CompanyName's Portal
* CompanyName's Operation System
* etc.
    ''')
    company_logo = fields.Binary('Company Logo', help="Due to browser cache, old logo may be still shown. To fix that, clear browser cache")

    wallpapers_count = fields.Integer('Wallpapers', readonly=True)

    new_documentation_website = fields.Char('Documentation Website', help='''Replaces links to documentation to custom website e.g.
* "Help" in Import tool
* "How-to" in paypal
* etc.
''')

    @api.model
    def get_values(self):
        res = super(Config, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        theme_id = ICPSudo.get_param("theme_kit.current_theme_id", default=False)
        if theme_id:
            theme_id = int(theme_id)
        favicon_id = ICPSudo.get_param("theme_kit.current_favicon_id", default=False)
        if favicon_id:
            favicon_id = int(favicon_id)
        page_title = ICPSudo.get_param("web_debranding.new_title", default=False)
        system_name = ICPSudo.get_param("web_debranding.new_name", default=False)
        new_documentation_website = ICPSudo.get_param("web_debranding.new_documentation_website", default=False)
        company_logo = self.env.user.company_id.logo
        wallpapers_count = self.env['ir.attachment'].search_count([('use_as_background', '=', True)])

        res.update(
            company_logo=company_logo,
            theme_id=int(theme_id),
            favicon_id=favicon_id,
            page_title=page_title,
            system_name=system_name,
            new_documentation_website=new_documentation_website,
            wallpapers_count=wallpapers_count
        )
        return res

    @api.multi
    def set_values(self):
        super(Config, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('theme_kit.current_theme_id', getattr(self, 'theme_id').id or '')
        ICPSudo.set_param('theme_kit.current_favicon_id', getattr(self, 'favicon_id').id or '')
        ICPSudo.set_param('web_debranding.new_title', getattr(self, 'page_title') or '')
        ICPSudo.set_param('web_debranding.new_name', getattr(self, 'system_name') or '')
        ICPSudo.set_param('web_debranding.new_documentation_website', getattr(self, 'new_documentation_website') or '')

        # set company logo
        self.env.user.company_id.logo = self.company_logo

        # set theme
        custom_css = self.env.ref('theme_kit.custom_css')
        code = ''
        if self.theme_id:
            code = self.theme_id.code
        arch = CUSTOM_CSS_ARCH % code
        custom_css.write({'arch': arch})

        # set favicon
        url = ''
        if self.favicon_id:
            url = self.favicon_id.url or self._attachment2url(self.favicon_id)
        ICPSudo.set_param('web_debranding.favicon_url', url)

    def _attachment2url(self, att):
        sha = hashlib.sha1(getattr(att, '__last_update').encode('utf-8')).hexdigest()[0:7]
        return '/web/image/%s-%s' % (att.id, sha)
