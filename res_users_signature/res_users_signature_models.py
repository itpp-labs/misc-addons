from openerp import api,models,fields,tools
from openerp.addons.email_template.email_template import mako_template_env

class res_users(models.Model):
    _inherit = 'res.users'

    signature_id = fields.Many2one('res.users.signature', string='Signature template', help='Keep empty to edit signature manually')



    @api.one
    @api.onchange('signature_id')
    def render_signature_id(self):
        print '#####################render_signature_id', self.partner_id, self
        if not self.signature_id:
            return
        mako = mako_template_env.from_string(tools.ustr(self.signature_id.template))
        html = mako.render({'user':self})
        self.signature = html


class res_users_signature(models.Model):
    _name = 'res.users.signature'

    name = fields.Char('Name')
    comment = fields.Text('Internal note')
    template = fields.Html('Template', help='''You can use variables:
* ${user.name}
* ${user.function} (job position)
* ${user.partner_id.company_id.name} (company in a partner form)
* ${user.company_id.name} (current company)
* ${user.email}
* ${user.phone}
* ${user.mobile}
* etc. (contact your administrator for further information)

You can use control structures:

% if user.mobile
    Mobile: ${user.mobile}
% endif

''')
    user_ids = fields.One2many('res.users', 'signature_id', string='Users')

    @api.one
    def write(self, vals):
        res = super(res_users_signature, self).write(vals)
        self.user_ids.render_signature_id()
        return res

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def write(self, vals):
        res = super(res_partner, self).write(vals)
        if self.user_ids:
            self.user_ids.render_signature_id()
        return res
