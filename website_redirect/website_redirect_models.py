from openerp import api, models, fields, SUPERUSER_ID
from openerp.http import request
import fnmatch
import werkzeug.utils

class website_redirect(models.Model):
    _name = 'website.redirect'

    _order = 'sequence,id'

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence')
    domain = fields.Char('Domain Name', placeholder='odoo.com', help='keep empty to apply rules for any domain')

    rule_ids = fields.One2many('website.redirect.rule', 'redirect_id', string='Rules')

class website_redirect(models.Model):
    _name = 'website.redirect.rule'

    _order = 'sequence,id'
    sequence = fields.Integer('Sequence')
    pattern = fields.Char('From', help='Unix shell-style wildcards. Check https://docs.python.org/2/library/fnmatch.html for details')
    target = fields.Char('To')
    redirect_id = fields.Many2one('website.redirect')

class ir_http(models.AbstractModel):
    _inherit = 'ir.http'

    def _dispatch(self):
        host = request.httprequest.environ.get('HTTP_HOST', '').split(':')[0]
        www, _, h = host.partition('.')
        if www == 'www':
            host = h
        path = request.httprequest.path
        redirect_ids = self.pool['website.redirect'].search(request.cr, SUPERUSER_ID, [])
        for redirect in self.pool['website.redirect'].browse(request.cr, SUPERUSER_ID, redirect_ids):
            if redirect.domain and redirect.domain != host:
                continue

            for rule in redirect.rule_ids:
                if fnmatch.fnmatch(path, rule.pattern):
                    code = 302
                    return werkzeug.utils.redirect(rule.target, code)
        return super(ir_http, self)._dispatch()
